"""
Procurement Management Views - PO, Quotations, Vendors
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from datetime import datetime

from .models import (
    PurchaseOrder, PurchaseOrderItem, Quotation, QuotationItem,
    Vendor, VendorProduct, Currency, Receiving, ReceivingItem, Product
)


def check_procurement_permission(user):
    """Check if user has procurement access (Warehouse Manager or Superuser)"""
    if user.is_superuser:
        return True
    if user.groups.filter(name='Warehouse Manager').exists():
        return True
    return False


@login_required
def procurement_dashboard(request):
    """Procurement dashboard - POs, Quotations, Vendors"""

    # Check permission
    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to access Procurement.')
        return redirect('dashboard')

    # Get statistics
    total_vendors = Vendor.objects.filter(is_active=True).count()
    total_pos = PurchaseOrder.objects.count()
    pending_pos = PurchaseOrder.objects.filter(status__in=['draft', 'submitted']).count()
    total_quotations = Quotation.objects.count()

    # Recent items
    recent_pos = PurchaseOrder.objects.all().order_by('-created_at')[:5]
    recent_quotations = Quotation.objects.all().order_by('-created_at')[:5]
    active_vendors = Vendor.objects.filter(is_active=True).order_by('name')[:10]

    context = {
        'page_title': 'Procurement Dashboard',
        'total_vendors': total_vendors,
        'total_pos': total_pos,
        'pending_pos': pending_pos,
        'total_quotations': total_quotations,
        'recent_pos': recent_pos,
        'recent_quotations': recent_quotations,
        'active_vendors': active_vendors,
    }
    return render(request, 'procurement/dashboard.html', context)


@login_required
def vendor_list(request):
    """List all vendors"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to access Vendors.')
        return redirect('dashboard')

    vendors = Vendor.objects.all().order_by('name')

    context = {
        'vendors': vendors,
        'page_title': 'Vendors',
    }
    return render(request, 'procurement/vendor_list.html', context)


@login_required
def po_list(request):
    """List all purchase orders"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to access Purchase Orders.')
        return redirect('dashboard')

    purchase_orders = PurchaseOrder.objects.all().order_by('-created_at')

    context = {
        'purchase_orders': purchase_orders,
        'page_title': 'Purchase Orders',
    }
    return render(request, 'procurement/po_list.html', context)


@login_required
def quotation_list(request):
    """List all quotations"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to access Quotations.')
        return redirect('dashboard')

    quotations = Quotation.objects.all().order_by('-created_at')

    context = {
        'quotations': quotations,
        'page_title': 'Quotations',
    }
    return render(request, 'procurement/quotation_list.html', context)
