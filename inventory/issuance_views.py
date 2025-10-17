from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import datetime

from .models import (
    ItemIssuance, ItemIssuanceLine, ItemRequest, ItemRequestLine,
    Product
)
from .utils import generate_issue_number


# ==================== Issuance Management ====================

@login_required
def issuance_list(request):
    """List all issuances - warehouse staff can view"""
    # Only warehouse staff, supervisors, and managers can view issuances
    can_view = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Staff', 'Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    if not can_view:
        messages.error(request, 'You do not have permission to view issuances.')
        return redirect('dashboard')

    issuances = ItemIssuance.objects.all().order_by('-issued_date')

    # Check if user can create issuance (supervisor or manager)
    can_create = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    context = {
        'issuances': issuances,
        'can_create': can_create,
    }
    return render(request, 'issuance/issuance_list.html', context)


@login_required
def issuance_create(request):
    """Create new issuance - warehouse supervisors can create"""
    # Only warehouse supervisors and managers can create issuances
    can_create = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    if not can_create:
        messages.error(request, 'You do not have permission to create issuances.')
        return redirect('issuance_list')

    # Get approved requests that have items remaining to be issued
    approved_requests = ItemRequest.objects.filter(status='approved')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        issued_to_id = request.POST.get('issued_to')

        if not request_id:
            messages.error(request, 'Please select a request.')
            context = {
                'approved_requests': approved_requests,
            }
            return render(request, 'issuance/issuance_create.html', context)

        item_request = get_object_or_404(ItemRequest, id=request_id)

        if item_request.status != 'approved':
            messages.error(request, 'Only approved requests can be issued.')
            return redirect('issuance_create')

        # Process the issuance
        try:
            with db_transaction.atomic():
                # Create the issuance
                issuance = ItemIssuance(
                    item_request=item_request,
                    issue_number=generate_issue_number(),
                    issued_by=request.user,
                    issued_to_id=issued_to_id or item_request.requested_by.id,
                    issued_date=timezone.now(),
                    status='completed',
                    notes=request.POST.get('notes', ''),
                )
                issuance.save()

                # Process each request line
                has_issuance = False
                for request_line in item_request.items.all():
                    # Get the issuance quantity from the form
                    qty_key = f'quantity_{request_line.id}'
                    quantity_issued = request.POST.get(qty_key, 0)

                    try:
                        quantity_issued = int(quantity_issued)
                    except (ValueError, TypeError):
                        quantity_issued = 0

                    if quantity_issued > 0:
                        # Check if quantity is valid
                        quantity_remaining = request_line.quantity_approved - request_line.quantity_issued

                        if quantity_issued > quantity_remaining:
                            raise ValueError(f'Issuance quantity for {request_line.product.name} exceeds remaining quantity')

                        # Check if enough stock available
                        if quantity_issued > request_line.product.quantity:
                            raise ValueError(f'Insufficient stock for {request_line.product.name}. Available: {request_line.product.quantity}')

                        # Create issuance line
                        ItemIssuanceLine.objects.create(
                            issuance=issuance,
                            request_line=request_line,
                            quantity_issued=quantity_issued,
                        )

                        # Update request line quantity_issued
                        request_line.quantity_issued += quantity_issued
                        request_line.save()

                        # Update product stock
                        request_line.product.quantity -= quantity_issued
                        request_line.product.save()

                        has_issuance = True

                if not has_issuance:
                    raise ValueError('No items to issue. Please enter quantities.')

                # Check if request is fully issued
                all_issued = True
                for request_line in item_request.items.all():
                    if request_line.quantity_issued < request_line.quantity_approved:
                        all_issued = False
                        break

                # Update request status
                if all_issued:
                    item_request.status = 'completed'
                else:
                    item_request.status = 'issued'  # Partially issued
                item_request.save()

                messages.success(request, f'Issuance {issuance.issue_number} created successfully!')
                return redirect('issuance_detail', issuance_id=issuance.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating issuance: {str(e)}')

    # GET request - show form
    context = {
        'approved_requests': approved_requests,
    }
    return render(request, 'issuance/issuance_create.html', context)


@login_required
def get_request_items(request, request_id):
    """AJAX endpoint to get request items for issuance form"""
    from django.http import JsonResponse

    item_request = get_object_or_404(ItemRequest, id=request_id)

    if item_request.status != 'approved':
        return JsonResponse({'error': 'Request is not approved'}, status=400)

    items = []
    for line in item_request.items.all():
        quantity_remaining = line.quantity_approved - line.quantity_issued
        items.append({
            'id': line.id,
            'product_name': line.product.name,
            'product_sku': line.product.sku or '-',
            'quantity_requested': line.quantity_requested,
            'quantity_approved': line.quantity_approved,
            'quantity_issued': line.quantity_issued,
            'quantity_remaining': quantity_remaining,
            'stock_available': line.product.quantity,
            'uom': line.product.unit_of_measure.abbreviation if line.product.unit_of_measure else '-',
        })

    return JsonResponse({
        'request_number': item_request.request_number,
        'requested_by': item_request.requested_by.get_full_name() or item_request.requested_by.username,
        'department': item_request.department.name if item_request.department else '-',
        'items': items,
    })


@login_required
def issuance_detail(request, issuance_id):
    """View details of an issuance"""
    can_view = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Warehouse Staff', 'Warehouse Supervisor', 'Warehouse Manager']).exists()
    )

    if not can_view:
        messages.error(request, 'You do not have permission to view issuances.')
        return redirect('dashboard')

    issuance = get_object_or_404(ItemIssuance, id=issuance_id)

    context = {
        'issuance': issuance,
    }
    return render(request, 'issuance/issuance_detail.html', context)
