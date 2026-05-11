from django import forms
from .models import Product
from .models import Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'stock', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'price': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'stock': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'image': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'e.g. Beverages'}),
            'icon': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'e.g. fa-coffee'}),
        }