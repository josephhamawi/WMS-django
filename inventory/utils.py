"""
Utility functions for the inventory app
"""
from datetime import datetime
from .models import PurchaseOrder, ItemRequest, ItemIssuance, Receiving, Quotation, Vendor, Product, Transfer


def generate_po_number():
    """Generate next PO number in format: PO000001"""
    prefix = "PO"

    # Get last PO
    last_po = PurchaseOrder.objects.filter(
        po_number__startswith=prefix
    ).order_by('-po_number').first()

    if last_po:
        try:
            # Extract number and increment
            last_number = int(last_po.po_number.replace(prefix, ''))
            new_number = last_number + 1
        except (ValueError, IndexError):
            # If the last PO number is not in expected format, count all POs
            new_number = PurchaseOrder.objects.count() + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:06d}"


def generate_request_number():
    """Generate next request number in format: REQ-YYYY-NNNN"""
    year = datetime.now().year
    prefix = f"REQ-{year}-"

    last_request = ItemRequest.objects.filter(
        request_number__startswith=prefix
    ).order_by('-request_number').first()

    if last_request:
        last_number = int(last_request.request_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"


def generate_issue_number():
    """Generate next issue number in format: ISS-YYYY-NNNN"""
    year = datetime.now().year
    prefix = f"ISS-{year}-"

    last_issue = ItemIssuance.objects.filter(
        issue_number__startswith=prefix
    ).order_by('-issue_number').first()

    if last_issue:
        last_number = int(last_issue.issue_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"


def generate_receiving_number():
    """Generate next receiving number in format: RCV-YYYY-NNNN"""
    year = datetime.now().year
    prefix = f"RCV-{year}-"

    # Count receivings for current year
    count = Receiving.objects.filter(
        created_at__year=year
    ).count()

    new_number = count + 1
    return f"{prefix}{new_number:04d}"


def generate_quotation_number():
    """Generate next quotation number in format: QTN-YYYY-NNNN"""
    year = datetime.now().year
    prefix = f"QTN-{year}-"

    last_quotation = Quotation.objects.filter(
        quotation_number__startswith=prefix
    ).order_by('-quotation_number').first()

    if last_quotation:
        last_number = int(last_quotation.quotation_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"


def generate_vendor_code():
    """Generate next vendor code in format: VEN-NNNN"""
    prefix = "VEN-"

    last_vendor = Vendor.objects.filter(
        code__startswith=prefix
    ).order_by('-code').first()

    if last_vendor:
        try:
            last_number = int(last_vendor.code.split('-')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            # If the last vendor code is not in expected format, count all vendors
            new_number = Vendor.objects.count() + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"


def generate_product_sku():
    """Generate next product SKU in format: PRD-NNNN"""
    prefix = "PRD-"

    last_product = Product.objects.filter(
        sku__startswith=prefix
    ).order_by('-sku').first()

    if last_product:
        try:
            last_number = int(last_product.sku.split('-')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            # If the last SKU is not in expected format, count all products
            new_number = Product.objects.count() + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"


def generate_transfer_number():
    """Generate next transfer number in format: TRF-YYYY-NNNN"""
    year = datetime.now().year
    prefix = f"TRF-{year}-"

    last_transfer = Transfer.objects.filter(
        transfer_number__startswith=prefix
    ).order_by('-transfer_number').first()

    if last_transfer:
        last_number = int(last_transfer.transfer_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"
