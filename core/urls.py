from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pos/', views.pos_terminal, name='pos_terminal'),
    path('checkout/', views.checkout, name='checkout'),
    
    path('inventory/', views.inventory, name='inventory'),
    path('inventory/add/', views.product_create, name='product_add'),
    path('inventory/edit/<int:pk>/', views.product_edit, name='product_edit'),
    
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/add/', views.category_create, name='category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),

    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_add, name='staff_add'),
    path('staff/edit/<int:user_id>/', views.staff_edit, name='staff_edit'),
    path('staff/delete/<int:user_id>/', views.staff_delete, name='staff_delete'),

    path('reports/', views.sales_reports, name='sales_reports'),
    path('order-detail/<int:pk>/', views.order_detail_json, name='order_detail_json'),
    path('settings/', views.shop_settings, name='settings'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('export/excel/', views.export_sales_excel, name='export_sales_excel'),
]