"""
Item Request Management Views - SAP Style
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from datetime import datetime

from .models import ItemRequest, ItemRequestLine, Product, Department, Site
from .forms import ItemRequestForm, ItemRequestLineFormSet
from .utils import generate_request_number


@login_required
def request_list(request):
    """List all item requests"""
    requests = ItemRequest.objects.all().order_by('-created_at')
    context = {
        'requests': requests,
        'page_title': 'Item Requests',
    }
    return render(request, 'requests/request_list.html', context)


@login_required
def request_add(request):
    """Add new item request - SAP style"""
    if request.method == 'POST':
        form = ItemRequestForm(request.POST)
        formset = ItemRequestLineFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Save request header
                    item_request = form.save(commit=False)
                    item_request.request_number = generate_request_number()
                    item_request.status = 'pending'
                    item_request.save()

                    # Save line items
                    formset.instance = item_request
                    formset.save()

                    messages.success(
                        request,
                        f'Item Request {item_request.request_number} created successfully!'
                    )
                    return redirect('request_detail', request_id=item_request.id)

            except Exception as e:
                messages.error(request, f'Error creating request: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize form with default values
        initial_data = {
            'requested_by': request.user,
            'requested_date': datetime.now(),
        }
        form = ItemRequestForm(initial=initial_data)
        formset = ItemRequestLineFormSet()

    context = {
        'form': form,
        'formset': formset,
        'page_title': 'New Item Request',
        'is_edit': False,
        'products': Product.objects.filter(quantity__gt=0).order_by('name'),
        'departments': Department.objects.filter(is_active=True),
        'sites': Site.objects.filter(is_active=True),
    }
    return render(request, 'requests/request_form.html', context)


@login_required
def request_edit(request, request_id):
    """Edit existing item request - SAP style"""
    item_request = get_object_or_404(ItemRequest, id=request_id)

    # Only allow editing if pending
    if item_request.status not in ['pending', 'draft']:
        messages.warning(request, 'Cannot edit request that is not in pending status.')
        return redirect('request_detail', request_id=request_id)

    # Check permission: requester can edit their own, department head can edit their department's requests
    is_requester = item_request.requested_by == request.user
    is_dept_head = (
        item_request.department and
        item_request.department.manager == request.user
    )
    is_authorized = is_requester or is_dept_head or request.user.is_superuser

    if not is_authorized:
        messages.error(request, 'You do not have permission to edit this request.')
        return redirect('request_detail', request_id=request_id)

    if request.method == 'POST':
        form = ItemRequestForm(request.POST, instance=item_request)
        formset = ItemRequestLineFormSet(request.POST, instance=item_request)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()

                    messages.success(
                        request,
                        f'Item Request {item_request.request_number} updated successfully!'
                    )
                    return redirect('request_detail', request_id=item_request.id)

            except Exception as e:
                messages.error(request, f'Error updating request: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ItemRequestForm(instance=item_request)
        formset = ItemRequestLineFormSet(instance=item_request)

    context = {
        'form': form,
        'formset': formset,
        'page_title': f'Edit Request {item_request.request_number}',
        'is_edit': True,
        'item_request': item_request,
        'products': Product.objects.all().order_by('name'),
        'departments': Department.objects.filter(is_active=True),
        'sites': Site.objects.filter(is_active=True),
    }
    return render(request, 'requests/request_form.html', context)


@login_required
def request_detail(request, request_id):
    """View item request details"""
    item_request = get_object_or_404(ItemRequest, id=request_id)
    lines = item_request.items.all()

    context = {
        'item_request': item_request,
        'lines': lines,
        'page_title': f'Request {item_request.request_number}',
    }
    return render(request, 'requests/request_detail.html', context)


@login_required
def request_delete(request, request_id):
    """Delete item request (only if pending)"""
    item_request = get_object_or_404(ItemRequest, id=request_id)

    if item_request.status != 'pending':
        messages.error(request, 'Cannot delete request that is not pending.')
        return redirect('request_list')

    # Check permission: requester can delete their own, department head can delete their department's requests
    is_requester = item_request.requested_by == request.user
    is_dept_head = (
        item_request.department and
        item_request.department.manager == request.user
    )
    is_authorized = is_requester or is_dept_head or request.user.is_superuser

    if not is_authorized:
        messages.error(request, 'You do not have permission to delete this request.')
        return redirect('request_list')

    if request.method == 'POST':
        request_number = item_request.request_number
        item_request.delete()
        messages.success(request, f'Request {request_number} deleted successfully.')
        return redirect('request_list')

    return render(request, 'requests/request_confirm_delete.html', {'item_request': item_request})


@login_required
def request_approve(request, request_id):
    """Approve item request (only department heads)"""
    item_request = get_object_or_404(ItemRequest, id=request_id)

    # Check if user is authorized to approve (department head or superuser)
    can_approve = (
        request.user.is_superuser or
        (item_request.department and item_request.department.manager == request.user)
    )

    if not can_approve:
        messages.error(request, 'You do not have permission to approve this request.')
        return redirect('request_detail', request_id=request_id)

    if item_request.status != 'pending':
        messages.error(request, 'Only pending requests can be approved.')
        return redirect('request_detail', request_id=request_id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                item_request.status = 'approved'
                item_request.approved_by = request.user
                item_request.approved_date = datetime.now()
                item_request.save()

                # Auto-approve all line items with requested quantities
                for line in item_request.items.all():
                    line.quantity_approved = line.quantity_requested
                    line.save()

                messages.success(
                    request,
                    f'Request {item_request.request_number} has been approved successfully!'
                )
                return redirect('request_detail', request_id=request_id)

        except Exception as e:
            messages.error(request, f'Error approving request: {str(e)}')

    return redirect('request_detail', request_id=request_id)


@login_required
def request_reject(request, request_id):
    """Reject item request (only department heads)"""
    item_request = get_object_or_404(ItemRequest, id=request_id)

    # Check if user is authorized to reject (department head or superuser)
    can_reject = (
        request.user.is_superuser or
        (item_request.department and item_request.department.manager == request.user)
    )

    if not can_reject:
        messages.error(request, 'You do not have permission to reject this request.')
        return redirect('request_detail', request_id=request_id)

    if item_request.status != 'pending':
        messages.error(request, 'Only pending requests can be rejected.')
        return redirect('request_detail', request_id=request_id)

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '').strip()

        if not rejection_reason:
            messages.error(request, 'Please provide a reason for rejection.')
            return redirect('request_detail', request_id=request_id)

        try:
            item_request.status = 'rejected'
            item_request.approved_by = request.user
            item_request.approved_date = datetime.now()
            item_request.rejection_reason = rejection_reason
            item_request.save()

            messages.warning(
                request,
                f'Request {item_request.request_number} has been rejected.'
            )
            return redirect('request_detail', request_id=request_id)

        except Exception as e:
            messages.error(request, f'Error rejecting request: {str(e)}')

    return redirect('request_detail', request_id=request_id)
