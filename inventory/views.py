from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.db.models import F, Q, Sum
from django.http import JsonResponse
from datetime import datetime

from .models import (
    Product, Department, Site, PurchaseOrder, PurchaseOrderItem,
    ItemRequest, ItemRequestLine, Receiving, ReceivingItem,
    ItemIssuance, ItemIssuanceLine, UnitOfMeasure
)
from .utils import (
    generate_po_number, generate_request_number,
    generate_issue_number, generate_receiving_number, generate_product_sku
)


# ==================== Dashboard ====================

def dashboard(request):
    """Main dashboard with overview"""
    # Get all products for the inventory table
    products = Product.objects.all().order_by('-id')
    low_stock = [p for p in products if p.is_low_stock]

    # Check if user has permission to add/edit inventory
    can_manage_inventory = False
    if request.user.is_authenticated:
        can_manage_inventory = (
            request.user.is_superuser or
            request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
        )

    context = {
        'products': products,
        'total_products': products.count(),
        'low_stock_count': len(low_stock),
        'pending_requests': ItemRequest.objects.filter(status='pending').count(),
        'pending_pos': PurchaseOrder.objects.filter(status__in=['draft', 'submitted']).count(),
        'can_manage_inventory': can_manage_inventory,
    }
    return render(request, 'dashboard.html', context)


@login_required
def inventory_dashboard(request):
    """Inventory & Warehouse Operations Dashboard"""
    # Get statistics
    total_products = Product.objects.count()
    low_stock = [p for p in Product.objects.all() if p.is_low_stock]
    low_stock_count = len(low_stock)

    pending_requests = ItemRequest.objects.filter(status='pending').count()
    total_issuances = ItemIssuance.objects.count()

    # Check permissions
    can_manage_inventory = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    can_create_issuance = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    context = {
        'page_title': 'Inventory & Warehouse Operations',
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'pending_requests': pending_requests,
        'total_issuances': total_issuances,
        'can_manage_inventory': can_manage_inventory,
        'can_create_issuance': can_create_issuance,
    }
    return render(request, 'inventory/dashboard.html', context)


# ==================== Inventory Management ====================

@login_required
def inventory_list(request):
    # All authenticated users can view inventory
    products = Product.objects.all().order_by('-id')

    # Check if user has permission to add/edit inventory
    can_manage_inventory = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    context = {
        'products': products,
        'can_manage_inventory': can_manage_inventory,
    }
    return render(request, 'inventory_list.html', context)

@login_required
def add_inventory(request):
    # Only Warehouse Supervisor and Warehouse Manager can add inventory
    can_add = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    if not can_add:
        messages.error(request, 'You do not have permission to add products.')
        return redirect('inventory_list')

    if request.method == 'POST':
        try:
            # Get and validate form data
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            quantity = request.POST.get('quantity', '').strip()
            location_id = request.POST.get('location', '')
            unit_of_measure_id = request.POST.get('unit_of_measure', '')

            # Validation
            if not name:
                raise ValidationError('Product name is required')
            if not description:
                raise ValidationError('Description is required')

            try:
                quantity = int(quantity)
                if quantity < 0:
                    raise ValidationError('Quantity cannot be negative')
            except (ValueError, TypeError):
                raise ValidationError('Quantity must be a valid number')

            # Auto-generate SKU
            sku = generate_product_sku()

            # Create product
            from .models import StorageLocation, UnitOfMeasure

            product = Product(
                name=name,
                sku=sku,
                description=description,
                quantity=quantity,
            )

            if location_id:
                product.location_id = location_id
            if unit_of_measure_id:
                product.unit_of_measure_id = unit_of_measure_id

            product.save()
            messages.success(request, f'Product "{name}" added successfully with SKU {sku}!')
            return redirect('inventory_list')

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')

    # Get dropdown data
    from .models import StorageLocation, UnitOfMeasure
    context = {
        'storage_locations': StorageLocation.objects.filter(is_active=True).order_by('code'),
        'units_of_measure': UnitOfMeasure.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'add_inventory.html', context)

@login_required
def update_inventory(request, product_id):
    # Only Warehouse Supervisor and Warehouse Manager can update inventory
    can_update = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    if not can_update:
        messages.error(request, 'You do not have permission to update products.')
        return redirect('inventory_list')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        try:
            # Get and validate form data
            name = request.POST.get('name', '').strip()
            sku = request.POST.get('sku', '').strip()
            description = request.POST.get('description', '').strip()
            quantity = request.POST.get('quantity', '').strip()
            location_id = request.POST.get('location', '')
            unit_of_measure_id = request.POST.get('unit_of_measure', '')

            # Validation
            if not name:
                raise ValidationError('Product name is required')
            if not description:
                raise ValidationError('Description is required')

            try:
                quantity = int(quantity)
                if quantity < 0:
                    raise ValidationError('Quantity cannot be negative')
            except (ValueError, TypeError):
                raise ValidationError('Quantity must be a valid number')

            # Update product
            product.name = name
            product.sku = sku if sku else None
            product.description = description
            product.quantity = quantity

            if location_id:
                product.location_id = location_id
            else:
                product.location = None

            if unit_of_measure_id:
                product.unit_of_measure_id = unit_of_measure_id
            else:
                product.unit_of_measure = None

            product.save()

            messages.success(request, f'Product "{name}" updated successfully!')
            return redirect('inventory_list')

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')

    # Get dropdown data
    from .models import StorageLocation, UnitOfMeasure
    context = {
        'product': product,
        'storage_locations': StorageLocation.objects.filter(is_active=True).order_by('code'),
        'units_of_measure': UnitOfMeasure.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'update_inventory.html', context)
