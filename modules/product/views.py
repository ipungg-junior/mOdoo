from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .models import Product
from .forms import ProductForm

class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'product_list.html', {'products': products})

class ProductCreateView(View):
    def get(self, request):
        form = ProductForm()
        return render(request, 'product_form.html', {'form': form, 'title': 'Create Product'})

    def post(self, request):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
        return render(request, 'product_form.html', {'form': form, 'title': 'Create Product'})

class ProductUpdateView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        return render(request, 'product_form.html', {'form': form, 'title': 'Update Product'})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
        return render(request, 'product_form.html', {'form': form, 'title': 'Update Product'})

class ProductDeleteView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'product_confirm_delete.html', {'product': product})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')