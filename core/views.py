import json
import uuid
import datetime
import openpyxl
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, F, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, Product, Category, ShopSetting
from .forms import ProductForm, CategoryForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ShopSetting
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout

@login_required
def dashboard(request):
    today = timezone.now().date()
    today_sales = Order.objects.filter(created_at__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    today_orders_count = Order.objects.filter(created_at__date=today).count()
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock__lt=5).count() 
    low_stock_list = Product.objects.filter(stock__lt=5)

    from .models import OrderItem 
    top_products = OrderItem.objects.values('product__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:5]

    recent_sales = Order.objects.order_by('-created_at')[:5]

    dates = []
    sales_data = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%d %b'))
        daily_total = Order.objects.filter(created_at__date=date).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        sales_data.append(float(daily_total))

    context = {
        'today_sales': today_sales,
        'today_orders_count': today_orders_count,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'low_stock_list': low_stock_list,
        'recent_sales': recent_sales,
        'dates': dates,
        'sales_data': sales_data,
    }
    return render(request, 'base.html', context)

@login_required
def pos_terminal(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'pos.html', {'products': products, 'categories': categories})

@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = data.get('cart', [])
        
        if not cart:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

        total = sum(item['price'] * item['quantity'] for item in cart)
        order = Order.objects.create(
            transaction_id=str(uuid.uuid4())[:8].upper(),
            total_amount=total
        )

        for item in cart:
            product = Product.objects.get(id=item['id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )
            
            product.stock -= item['quantity']
            product.save()

        return JsonResponse({'status': 'success', 'order_id': order.transaction_id})



def is_manager_or_admin(user):
    return user.is_superuser or user.groups.filter(name='Manager').exists()

@user_passes_test(is_manager_or_admin, login_url='dashboard')
def inventory(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'inventory.html', {'products': products})

def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inventory')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form, 'title': 'Add New Product'})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'title': 'Edit Product'})

def categories_list(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})

def sales_reports(request):
    orders_list = Order.objects.all().order_by('-created_at')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        orders_list = orders_list.filter(created_at__date__gte=start_date)
    if end_date:
        orders_list = orders_list.filter(created_at__date__lte=end_date)

    
    total_sales_amount = orders_list.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders_count = orders_list.count()
    
    today = timezone.now().date()
    today_sales = Order.objects.filter(created_at__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

   
    top_products = OrderItem.objects.filter(order__in=orders_list).values('product__name', 'product__category__name') \
        .annotate(total_qty=Sum('quantity')) \
        .order_by('-total_qty')[:5]

    
    category_sales = OrderItem.objects.filter(order__in=orders_list).values('product__category__name') \
        .annotate(total_amount=Sum(F('quantity') * F('price'))) \
        .order_by('-total_amount')

    
    context = {
        'orders': orders_list, 
        'total_sales_amount': total_sales_amount,
        'total_orders_count': total_orders_count,
        'today_sales': today_sales,
        'top_products': top_products,
        'category_sales': category_sales,
    }
    
    return render(request, 'sales_reports.html', context)

def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories_list')
    else:
        form = CategoryForm()
   
    return render(request, 'product_form.html', {
        'form': form, 
        'title': 'Add New Category',
        'cancel_url': 'categories_list' 
    })

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'product_form.html', {
        'form': form, 
        'title': 'Edit Category',
        'cancel_url': 'categories_list'
    })

def order_detail_json(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    items = [{
        'product_name': item.product.name,
        'quantity': item.quantity,
        'price': float(item.price),
        'subtotal': float(item.price * item.quantity)
    } for item in order.items.all()]
    
    return JsonResponse({
        'transaction_id': order.transaction_id,
        'created_at': order.created_at.strftime("%d %b %Y | %I:%M %p"),
        'total_amount': float(order.total_amount),
        'items': items
    })


def staff_list(request):
    staffs = User.objects.all().order_by('-date_joined')
    return render(request, 'staff_list.html', {'staffs': staffs})

def staff_add(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_list')
    else:
        form = UserCreationForm()
    return render(request, 'product_form.html', {
        'form': form, 
        'title': 'Add New Staff',
        'cancel_url': 'staff_list'
    })

def shop_settings(request):
    setting, created = ShopSetting.objects.get_or_create(id=1)
    
    if request.method == "POST":
        setting.shop_name = request.POST.get('shop_name')
        setting.phone = request.POST.get('phone')
        setting.address = request.POST.get('address')
        setting.footer_receipt = request.POST.get('footer_receipt')
        
        if request.FILES.get('logo'):
            setting.logo = request.FILES.get('logo')
            
        setting.save()
        return redirect('dashboard') 
        
    return render(request, 'settings.html', {'setting': setting})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def staff_edit(request, user_id):
    staff = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        staff.username = request.POST.get('username')
        staff.is_active = 'is_active' in request.POST
        staff.save()
        messages.success(request, f"{staff.username}'s profile updated!")
        return redirect('staff_list')
        
    return render(request, 'staff_edit.html', {'staff': staff})

@user_passes_test(is_admin)
def staff_delete(request, user_id):
    staff = get_object_or_404(User, id=user_id)
    if staff.is_superuser:
        messages.error(request, "Admin account ကို ဖျက်လို့မရပါဘူးဗျာ။")
    else:
        staff.delete()
        messages.success(request, "ဝန်ထမ်းစာရင်းကို ဖျက်လိုက်ပါပြီ။")
    return redirect('staff_list')

def logout_view(request):
    logout(request)
    messages.success(request, "အောင်မြင်စွာ Logout လုပ်ပြီးပါပြီ။")
    return redirect('login')

def export_sales_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    orders = Order.objects.all().order_by('-created_at')

    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    headers = ['Transaction ID', 'Date', 'Total Amount']
    ws.append(headers)


    for order in orders:
        ws.append([order.transaction_id, order.created_at.replace(tzinfo=None), order.total_amount])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    wb.save(response)
    return response


def settings_view(request):
    setting = ShopSetting.objects.first()
    if not setting:
        setting = ShopSetting.objects.create(shop_name="My POS Shop")

    if request.method == 'POST':
        setting.shop_name = request.POST.get('shop_name')
        setting.phone = request.POST.get('phone')
        setting.address = request.POST.get('address')
        setting.currency = request.POST.get('currency', 'MMK')
        
        try:
            setting.tax_rate = float(request.POST.get('tax_rate', 0))
            setting.low_stock_limit = int(request.POST.get('low_stock_limit', 5))
        except (ValueError, TypeError):
            pass 

        setting.footer_receipt = request.POST.get('footer_receipt')

       
        if request.FILES.get('logo'):
            setting.logo = request.FILES.get('logo')
            setting.save()
            messages.success(request, "ဆိုင်အချက်အလက်များကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
        return redirect('settings') 

    return render(request, 'settings.html', {'setting': setting})

def pos_terminal(request):
    setting = ShopSetting.objects.first() 
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'setting': setting, 
    }
    return render(request, 'pos.html', context)