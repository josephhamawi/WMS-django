"""
Transfer Management Views - Warehouse location transfers
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from .models import Transfer, Product, StorageLocation
from .utils import generate_transfer_number


@login_required
def transfer_list(request):
    """List all transfers"""
    transfers = Transfer.objects.all().order_by('-created_at')

    # Check if user can create transfers (Warehouse Supervisor/Manager)
    can_create_transfer = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    context = {
        'transfers': transfers,
        'can_create_transfer': can_create_transfer,
        'page_title': 'Transfers',
    }
    return render(request, 'transfer/transfer_list.html', context)


@login_required
def transfer_create(request):
    """Create a new transfer"""
    # Only Warehouse Supervisor and Warehouse Manager can create transfers
    can_create = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    if not can_create:
        messages.error(request, 'You do not have permission to create transfers.')
        return redirect('transfer_list')

    if request.method == 'POST':
        try:
            # Get form data
            product_id = request.POST.get('product')
            quantity = request.POST.get('quantity')
            from_location_id = request.POST.get('from_location')
            to_location_id = request.POST.get('to_location')
            notes = request.POST.get('notes', '').strip()

            # Validation
            if not product_id:
                raise ValueError('Product is required')
            if not from_location_id:
                raise ValueError('Source location is required')
            if not to_location_id:
                raise ValueError('Destination location is required')

            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError('Quantity must be greater than 0')
            except (ValueError, TypeError):
                raise ValueError('Quantity must be a valid number')

            # Check if source and destination are different
            if from_location_id == to_location_id:
                raise ValueError('Source and destination locations must be different')

            # Get product and locations
            product = get_object_or_404(Product, id=product_id)
            from_location = get_object_or_404(StorageLocation, id=from_location_id)
            to_location = get_object_or_404(StorageLocation, id=to_location_id)

            # Check if product is currently at the from_location
            if product.location != from_location:
                raise ValueError(f'Product is not currently at {from_location.code}. Current location: {product.location.code if product.location else "Not Set"}')

            # Check if there's enough quantity
            if product.quantity < quantity:
                raise ValueError(f'Insufficient quantity. Available: {product.quantity}')

            # Auto-generate transfer number
            transfer_number = generate_transfer_number()

            # Create transfer
            with transaction.atomic():
                transfer = Transfer.objects.create(
                    transfer_number=transfer_number,
                    product=product,
                    quantity=quantity,
                    from_location=from_location,
                    to_location=to_location,
                    requested_by=request.user,
                    notes=notes,
                    status='pending'
                )

            messages.success(request, f'Transfer {transfer_number} created successfully!')
            return redirect('transfer_detail', transfer_id=transfer.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating transfer: {str(e)}')

    # Get products and locations for dropdowns
    products = Product.objects.all().order_by('name')
    locations = StorageLocation.objects.filter(is_active=True).order_by('code')

    context = {
        'products': products,
        'locations': locations,
        'page_title': 'Create Transfer',
    }
    return render(request, 'transfer/transfer_create.html', context)


@login_required
def transfer_detail(request, transfer_id):
    """View transfer details"""
    transfer = get_object_or_404(Transfer, id=transfer_id)

    # Check if user can complete transfers
    can_complete_transfer = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    context = {
        'transfer': transfer,
        'can_complete_transfer': can_complete_transfer,
        'page_title': f'Transfer {transfer.transfer_number}',
    }
    return render(request, 'transfer/transfer_detail.html', context)


@login_required
def transfer_complete(request, transfer_id):
    """Complete a transfer - actually move the inventory"""
    transfer = get_object_or_404(Transfer, id=transfer_id)

    # Only Warehouse Supervisor and Warehouse Manager can complete transfers
    can_complete = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    if not can_complete:
        messages.error(request, 'You do not have permission to complete transfers.')
        return redirect('transfer_detail', transfer_id=transfer_id)

    # Check if transfer is already completed or cancelled
    if transfer.status != 'pending':
        messages.error(request, f'Transfer is already {transfer.status}')
        return redirect('transfer_detail', transfer_id=transfer_id)

    try:
        with transaction.atomic():
            # Update product location
            product = transfer.product

            # Verify product is still at from_location
            if product.location != transfer.from_location:
                raise ValueError(f'Product is no longer at {transfer.from_location.code}')

            # Update product location
            product.location = transfer.to_location
            product.save()

            # Update transfer status
            transfer.status = 'completed'
            transfer.transferred_by = request.user
            transfer.transfer_date = timezone.now()
            transfer.save()

        messages.success(request, f'Transfer {transfer.transfer_number} completed successfully! {product.name} moved from {transfer.from_location.code} to {transfer.to_location.code}')
        return redirect('transfer_detail', transfer_id=transfer_id)

    except Exception as e:
        messages.error(request, f'Error completing transfer: {str(e)}')
        return redirect('transfer_detail', transfer_id=transfer_id)


@login_required
def transfer_cancel(request, transfer_id):
    """Cancel a transfer"""
    transfer = get_object_or_404(Transfer, id=transfer_id)

    # Only Warehouse Supervisor and Warehouse Manager can cancel transfers
    can_cancel = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    if not can_cancel:
        messages.error(request, 'You do not have permission to cancel transfers.')
        return redirect('transfer_detail', transfer_id=transfer_id)

    # Check if transfer is already completed or cancelled
    if transfer.status != 'pending':
        messages.error(request, f'Transfer is already {transfer.status}')
        return redirect('transfer_detail', transfer_id=transfer_id)

    try:
        transfer.status = 'cancelled'
        transfer.save()

        messages.success(request, f'Transfer {transfer.transfer_number} cancelled successfully!')
        return redirect('transfer_detail', transfer_id=transfer_id)

    except Exception as e:
        messages.error(request, f'Error cancelling transfer: {str(e)}')
        return redirect('transfer_detail', transfer_id=transfer_id)
