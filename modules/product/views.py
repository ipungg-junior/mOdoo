from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .models import Product
from .forms import ProductForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Permission

class ProductListView(PermissionRequiredMixin, View):
    group_required = 'group_access_product'
    permission_required = 'product.view_product'
    def get(self, request):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        products = Product.objects.all()
        return render(request, 'product_list.html', {'products': products})

class ProductCreateView(PermissionRequiredMixin, View):
    group_required = 'group_access_product'
    permission_required = 'product.add_product'
    def get(self, request):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        form = ProductForm()
        return render(request, 'product_form.html', {'form': form, 'title': 'Create Product'})

    def post(self, request):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
        return render(request, 'product_form.html', {'form': form, 'title': 'Create Product'})

class ProductUpdateView(PermissionRequiredMixin, View):
    group_required = 'group_access_product'
    permission_required = ['product.change_product']
    def get(self, request, pk):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        return render(request, 'product_form.html', {'form': form, 'title': 'Change Product'})

    def post(self, request, pk):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user  # Update the creator on edit
            product.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
        return render(request, 'product_form.html', {'form': form, 'title': 'Update Product'})

class ProductDeleteView(PermissionRequiredMixin, View):
    group_required = 'group_access_product'
    permission_required = 'product.delete_product'
    def get(self, request, pk):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'product_confirm_delete.html', {'product': product})

    def post(self, request, pk):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')