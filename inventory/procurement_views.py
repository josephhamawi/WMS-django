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
from .utils import generate_vendor_code, generate_po_number, generate_quotation_number


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


@login_required
def vendor_add(request):
    """Add a new vendor"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to add vendors.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            contact_person = request.POST.get('contact_person', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            payment_terms = request.POST.get('payment_terms', '').strip()
            currency_id = request.POST.get('currency', '')
            is_active = request.POST.get('is_active') == 'on'

            # Validation
            if not name:
                raise ValueError('Vendor name is required')

            # Check for duplicate name
            if Vendor.objects.filter(name=name).exists():
                raise ValueError(f'Vendor name "{name}" already exists')

            # Auto-generate vendor code
            code = generate_vendor_code()

            # Create vendor
            vendor = Vendor(
                name=name,
                code=code,
                contact_person=contact_person,
                email=email,
                phone=phone,
                address=address,
                payment_terms=payment_terms,
                is_active=is_active,
            )

            if currency_id:
                vendor.currency_id = currency_id

            vendor.save()
            messages.success(request, f'Vendor "{name}" added successfully with code {code}!')
            return redirect('vendor_list')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error adding vendor: {str(e)}')

    # Get currencies for dropdown
    currencies = Currency.objects.filter(is_active=True).order_by('code')

    context = {
        'currencies': currencies,
        'page_title': 'Add New Vendor',
    }
    return render(request, 'procurement/vendor_add.html', context)


@login_required
def vendor_update(request, vendor_id):
    """Update an existing vendor"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to update vendors.')
        return redirect('dashboard')

    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            contact_person = request.POST.get('contact_person', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            payment_terms = request.POST.get('payment_terms', '').strip()
            currency_id = request.POST.get('currency', '')
            is_active = request.POST.get('is_active') == 'on'

            # Validation
            if not name:
                raise ValueError('Vendor name is required')
            if not code:
                raise ValueError('Vendor code is required')

            # Check for duplicates (excluding current vendor)
            if Vendor.objects.filter(code=code).exclude(id=vendor_id).exists():
                raise ValueError(f'Vendor code "{code}" already exists')
            if Vendor.objects.filter(name=name).exclude(id=vendor_id).exists():
                raise ValueError(f'Vendor name "{name}" already exists')

            # Update vendor
            vendor.name = name
            vendor.code = code
            vendor.contact_person = contact_person
            vendor.email = email
            vendor.phone = phone
            vendor.address = address
            vendor.payment_terms = payment_terms
            vendor.is_active = is_active

            if currency_id:
                vendor.currency_id = currency_id
            else:
                vendor.currency = None

            vendor.save()
            messages.success(request, f'Vendor "{name}" updated successfully!')
            return redirect('vendor_list')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error updating vendor: {str(e)}')

    # Get currencies for dropdown
    currencies = Currency.objects.filter(is_active=True).order_by('code')

    context = {
        'vendor': vendor,
        'currencies': currencies,
        'page_title': 'Update Vendor',
    }
    return render(request, 'procurement/vendor_update.html', context)


@login_required
def vendor_delete(request, vendor_id):
    """Delete a vendor"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to delete vendors.')
        return redirect('dashboard')

    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        vendor_name = vendor.name
        vendor.delete()
        messages.success(request, f'Vendor "{vendor_name}" deleted successfully!')
        return redirect('vendor_list')

    context = {
        'vendor': vendor,
        'page_title': 'Delete Vendor',
    }
    return render(request, 'procurement/vendor_delete.html', context)


# ==================== Purchase Order CRUD ====================

@login_required
def po_add(request):
    """Create a new Purchase Order"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to create purchase orders.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get PO header data
                vendor_id = request.POST.get('vendor')
                external_po_number = request.POST.get('external_po_number', '').strip()
                order_date = request.POST.get('order_date')
                expected_delivery = request.POST.get('expected_delivery')
                delivery_address = request.POST.get('delivery_address', '').strip()
                payment_terms = request.POST.get('payment_terms', '').strip()
                notes = request.POST.get('notes', '').strip()
                currency_id = request.POST.get('currency')

                # Validation
                if not vendor_id:
                    raise ValueError('Vendor is required')

                vendor = get_object_or_404(Vendor, id=vendor_id)

                # Auto-generate PO number
                po_number = generate_po_number()

                # Create PO
                po = PurchaseOrder(
                    po_number=po_number,
                    external_po_number=external_po_number,
                    vendor=vendor,
                    order_date=order_date if order_date else timezone.now().date(),
                    expected_delivery=expected_delivery if expected_delivery else None,
                    delivery_address=delivery_address,
                    payment_terms=payment_terms,
                    notes=notes,
                    status='draft',
                    created_by=request.user,
                )

                if currency_id:
                    po.currency_id = currency_id
                elif vendor.currency:
                    po.currency = vendor.currency

                po.save()

                # Process line items
                item_count = 0
                for key in request.POST:
                    if key.startswith('product_'):
                        index = key.split('_')[1]
                        product_id = request.POST.get(f'product_{index}')
                        quantity = request.POST.get(f'quantity_{index}', '0')
                        unit_price = request.POST.get(f'unit_price_{index}', '0')

                        if product_id and quantity and float(quantity) > 0:
                            product = get_object_or_404(Product, id=product_id)
                            PurchaseOrderItem.objects.create(
                                purchase_order=po,
                                product=product,
                                quantity_ordered=int(quantity),
                                unit_price=float(unit_price),
                            )
                            item_count += 1

                if item_count == 0:
                    raise ValueError('At least one line item is required')

                messages.success(request, f'Purchase Order {po.po_number} created successfully with {item_count} items!')
                return redirect('po_detail', po_id=po.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating purchase order: {str(e)}')

    # Get data for form
    vendors = Vendor.objects.filter(is_active=True).order_by('name')
    products = Product.objects.all().order_by('name')
    currencies = Currency.objects.filter(is_active=True).order_by('code')

    context = {
        'vendors': vendors,
        'products': products,
        'currencies': currencies,
        'page_title': 'Create Purchase Order',
    }
    return render(request, 'procurement/po_add.html', context)


@login_required
def po_detail(request, po_id):
    """View Purchase Order details"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to view purchase orders.')
        return redirect('dashboard')

    po = get_object_or_404(PurchaseOrder, id=po_id)
    items = po.items.all()

    context = {
        'po': po,
        'items': items,
        'page_title': f'Purchase Order {po.po_number}',
        'can_edit': po.status in ['draft', 'submitted'],
        'can_delete': po.status == 'draft',
    }
    return render(request, 'procurement/po_detail.html', context)


@login_required
def po_edit(request, po_id):
    """Edit an existing Purchase Order"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to edit purchase orders.')
        return redirect('dashboard')

    po = get_object_or_404(PurchaseOrder, id=po_id)

    # Can only edit draft or submitted POs
    if po.status not in ['draft', 'submitted']:
        messages.error(request, f'Cannot edit PO in {po.get_status_display()} status.')
        return redirect('po_detail', po_id=po.id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update PO header
                vendor_id = request.POST.get('vendor')
                po.external_po_number = request.POST.get('external_po_number', '').strip()
                po.order_date = request.POST.get('order_date') or timezone.now().date()
                expected_delivery = request.POST.get('expected_delivery')
                po.expected_delivery = expected_delivery if expected_delivery else None
                po.delivery_address = request.POST.get('delivery_address', '').strip()
                po.payment_terms = request.POST.get('payment_terms', '').strip()
                po.notes = request.POST.get('notes', '').strip()
                currency_id = request.POST.get('currency')

                if vendor_id:
                    po.vendor_id = vendor_id
                if currency_id:
                    po.currency_id = currency_id

                po.save()

                # Delete existing items
                po.items.all().delete()

                # Add new items
                item_count = 0
                for key in request.POST:
                    if key.startswith('product_'):
                        index = key.split('_')[1]
                        product_id = request.POST.get(f'product_{index}')
                        quantity = request.POST.get(f'quantity_{index}', '0')
                        unit_price = request.POST.get(f'unit_price_{index}', '0')

                        if product_id and quantity and float(quantity) > 0:
                            product = get_object_or_404(Product, id=product_id)
                            PurchaseOrderItem.objects.create(
                                purchase_order=po,
                                product=product,
                                quantity_ordered=int(quantity),
                                unit_price=float(unit_price),
                            )
                            item_count += 1

                if item_count == 0:
                    raise ValueError('At least one line item is required')

                messages.success(request, f'Purchase Order {po.po_number} updated successfully!')
                return redirect('po_detail', po_id=po.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error updating purchase order: {str(e)}')

    # Get data for form
    vendors = Vendor.objects.filter(is_active=True).order_by('name')
    products = Product.objects.all().order_by('name')
    currencies = Currency.objects.filter(is_active=True).order_by('code')
    items = po.items.all()

    context = {
        'po': po,
        'items': items,
        'vendors': vendors,
        'products': products,
        'currencies': currencies,
        'page_title': f'Edit Purchase Order {po.po_number}',
    }
    return render(request, 'procurement/po_edit.html', context)


@login_required
def po_delete(request, po_id):
    """Delete a Purchase Order"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to delete purchase orders.')
        return redirect('dashboard')

    po = get_object_or_404(PurchaseOrder, id=po_id)

    # Can only delete draft POs
    if po.status != 'draft':
        messages.error(request, f'Cannot delete PO in {po.get_status_display()} status.')
        return redirect('po_detail', po_id=po.id)

    if request.method == 'POST':
        po_number = po.po_number
        po.delete()
        messages.success(request, f'Purchase Order {po_number} deleted successfully!')
        return redirect('po_list')

    context = {
        'po': po,
        'page_title': 'Delete Purchase Order',
    }
    return render(request, 'procurement/po_delete.html', context)


@login_required
def po_change_status(request, po_id):
    """Change Purchase Order status"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to change PO status.')
        return redirect('dashboard')

    po = get_object_or_404(PurchaseOrder, id=po_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(PurchaseOrder.STATUS_CHOICES):
            old_status = po.get_status_display()
            po.status = new_status

            # Set approved date and user if status is approved
            if new_status == 'approved' and not po.approved_by:
                po.approved_by = request.user
                po.approved_date = timezone.now()

            po.save()
            messages.success(request, f'PO status changed from {old_status} to {po.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')

    return redirect('po_detail', po_id=po.id)


# ==================== Quotation CRUD ====================

@login_required
def quotation_add(request):
    """Create a new Quotation/RFQ"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to create quotations.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get quotation header data
                vendor_id = request.POST.get('vendor')
                request_date = request.POST.get('request_date')
                valid_until = request.POST.get('valid_until')
                quotation_date = request.POST.get('quotation_date')
                notes = request.POST.get('notes', '').strip()
                currency_id = request.POST.get('currency')
                status = request.POST.get('status', 'draft')

                # Validation
                if not vendor_id:
                    raise ValueError('Vendor is required')

                vendor = get_object_or_404(Vendor, id=vendor_id)

                # Auto-generate quotation number
                quotation_number = generate_quotation_number()

                # Create Quotation
                quotation = Quotation(
                    quotation_number=quotation_number,
                    vendor=vendor,
                    request_date=request_date if request_date else timezone.now().date(),
                    valid_until=valid_until if valid_until else None,
                    quotation_date=quotation_date if quotation_date else None,
                    notes=notes,
                    status=status,
                    created_by=request.user,
                )

                if currency_id:
                    quotation.currency_id = currency_id
                elif vendor.currency:
                    quotation.currency = vendor.currency
                else:
                    # Default to first active currency
                    default_currency = Currency.objects.filter(is_active=True).first()
                    if default_currency:
                        quotation.currency = default_currency

                quotation.save()

                # Process line items
                item_count = 0
                for key in request.POST:
                    if key.startswith('product_'):
                        index = key.split('_')[1]
                        product_id = request.POST.get(f'product_{index}')
                        quantity = request.POST.get(f'quantity_{index}', '0')
                        unit_price = request.POST.get(f'unit_price_{index}', '0')
                        vendor_sku = request.POST.get(f'vendor_sku_{index}', '').strip()
                        lead_time = request.POST.get(f'lead_time_{index}', '0')

                        if product_id and quantity and float(quantity) > 0:
                            product = get_object_or_404(Product, id=product_id)
                            QuotationItem.objects.create(
                                quotation=quotation,
                                product=product,
                                quantity=int(quantity),
                                unit_price=float(unit_price) if unit_price else 0,
                                vendor_sku=vendor_sku,
                                lead_time_days=int(lead_time) if lead_time else 0,
                            )
                            item_count += 1

                if item_count == 0:
                    raise ValueError('At least one line item is required')

                messages.success(request, f'Quotation {quotation.quotation_number} created successfully with {item_count} items!')
                return redirect('quotation_detail', quotation_id=quotation.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating quotation: {str(e)}')

    # Get data for form
    vendors = Vendor.objects.filter(is_active=True).order_by('name')
    products = Product.objects.all().order_by('name')
    currencies = Currency.objects.filter(is_active=True).order_by('code')

    context = {
        'vendors': vendors,
        'products': products,
        'currencies': currencies,
        'status_choices': Quotation.STATUS_CHOICES,
        'page_title': 'Create Quotation/RFQ',
    }
    return render(request, 'procurement/quotation_add.html', context)


@login_required
def quotation_detail(request, quotation_id):
    """View Quotation details"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to view quotations.')
        return redirect('dashboard')

    quotation = get_object_or_404(Quotation, id=quotation_id)
    items = quotation.items.all()

    context = {
        'quotation': quotation,
        'items': items,
        'page_title': f'Quotation {quotation.quotation_number}',
        'can_edit': quotation.status in ['draft', 'sent'],
        'can_delete': quotation.status == 'draft',
        'can_convert': quotation.status == 'received',
    }
    return render(request, 'procurement/quotation_detail.html', context)


@login_required
def quotation_edit(request, quotation_id):
    """Edit an existing Quotation"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to edit quotations.')
        return redirect('dashboard')

    quotation = get_object_or_404(Quotation, id=quotation_id)

    # Can only edit draft or sent quotations
    if quotation.status not in ['draft', 'sent', 'received']:
        messages.error(request, f'Cannot edit quotation in {quotation.get_status_display()} status.')
        return redirect('quotation_detail', quotation_id=quotation.id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update quotation header
                vendor_id = request.POST.get('vendor')
                quotation.request_date = request.POST.get('request_date') or timezone.now().date()
                valid_until = request.POST.get('valid_until')
                quotation.valid_until = valid_until if valid_until else None
                quotation_date = request.POST.get('quotation_date')
                quotation.quotation_date = quotation_date if quotation_date else None
                quotation.notes = request.POST.get('notes', '').strip()
                quotation.status = request.POST.get('status', quotation.status)
                currency_id = request.POST.get('currency')

                if vendor_id:
                    quotation.vendor_id = vendor_id
                if currency_id:
                    quotation.currency_id = currency_id

                quotation.save()

                # Delete existing items
                quotation.items.all().delete()

                # Add new items
                item_count = 0
                for key in request.POST:
                    if key.startswith('product_'):
                        index = key.split('_')[1]
                        product_id = request.POST.get(f'product_{index}')
                        quantity = request.POST.get(f'quantity_{index}', '0')
                        unit_price = request.POST.get(f'unit_price_{index}', '0')
                        vendor_sku = request.POST.get(f'vendor_sku_{index}', '').strip()
                        lead_time = request.POST.get(f'lead_time_{index}', '0')

                        if product_id and quantity and float(quantity) > 0:
                            product = get_object_or_404(Product, id=product_id)
                            QuotationItem.objects.create(
                                quotation=quotation,
                                product=product,
                                quantity=int(quantity),
                                unit_price=float(unit_price) if unit_price else 0,
                                vendor_sku=vendor_sku,
                                lead_time_days=int(lead_time) if lead_time else 0,
                            )
                            item_count += 1

                if item_count == 0:
                    raise ValueError('At least one line item is required')

                messages.success(request, f'Quotation {quotation.quotation_number} updated successfully!')
                return redirect('quotation_detail', quotation_id=quotation.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error updating quotation: {str(e)}')

    # Get data for form
    vendors = Vendor.objects.filter(is_active=True).order_by('name')
    products = Product.objects.all().order_by('name')
    currencies = Currency.objects.filter(is_active=True).order_by('code')
    items = quotation.items.all()

    context = {
        'quotation': quotation,
        'items': items,
        'vendors': vendors,
        'products': products,
        'currencies': currencies,
        'status_choices': Quotation.STATUS_CHOICES,
        'page_title': f'Edit Quotation {quotation.quotation_number}',
    }
    return render(request, 'procurement/quotation_edit.html', context)


@login_required
def quotation_delete(request, quotation_id):
    """Delete a Quotation"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to delete quotations.')
        return redirect('dashboard')

    quotation = get_object_or_404(Quotation, id=quotation_id)

    # Can only delete draft quotations
    if quotation.status != 'draft':
        messages.error(request, f'Cannot delete quotation in {quotation.get_status_display()} status.')
        return redirect('quotation_detail', quotation_id=quotation.id)

    if request.method == 'POST':
        quotation_number = quotation.quotation_number
        quotation.delete()
        messages.success(request, f'Quotation {quotation_number} deleted successfully!')
        return redirect('quotation_list')

    context = {
        'quotation': quotation,
        'page_title': 'Delete Quotation',
    }
    return render(request, 'procurement/quotation_delete.html', context)


@login_required
def quotation_to_po(request, quotation_id):
    """Convert Quotation to Purchase Order"""

    if not check_procurement_permission(request.user):
        messages.error(request, 'You do not have permission to convert quotations.')
        return redirect('dashboard')

    quotation = get_object_or_404(Quotation, id=quotation_id)

    # Can only convert received quotations
    if quotation.status != 'received':
        messages.error(request, 'Only received quotations can be converted to PO.')
        return redirect('quotation_detail', quotation_id=quotation.id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create PO from quotation
                po_number = generate_po_number()

                po = PurchaseOrder.objects.create(
                    po_number=po_number,
                    vendor=quotation.vendor,
                    currency=quotation.currency,
                    order_date=timezone.now().date(),
                    expected_delivery=quotation.valid_until,
                    payment_terms=quotation.vendor.payment_terms if quotation.vendor else '',
                    notes=f'Created from Quotation {quotation.quotation_number}\n{quotation.notes}',
                    status='draft',
                    created_by=request.user,
                )

                # Copy items from quotation to PO
                for item in quotation.items.all():
                    PurchaseOrderItem.objects.create(
                        purchase_order=po,
                        product=item.product,
                        quantity_ordered=item.quantity,
                        unit_price=item.unit_price,
                    )

                # Mark quotation as accepted
                quotation.status = 'accepted'
                quotation.save()

                messages.success(request, f'Purchase Order {po.po_number} created from Quotation {quotation.quotation_number}!')
                return redirect('po_detail', po_id=po.id)

        except Exception as e:
            messages.error(request, f'Error converting quotation: {str(e)}')
            return redirect('quotation_detail', quotation_id=quotation.id)

    context = {
        'quotation': quotation,
        'page_title': 'Convert Quotation to PO',
    }
    return render(request, 'procurement/quotation_to_po.html', context)
