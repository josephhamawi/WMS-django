"""
Utility functions for the inventory app
"""
from datetime import datetime
from .models import PurchaseOrder, ItemRequest, ItemIssuance, Receiving, Quotation


def generate_po_number():
    """Generate next PO number in format: PO-YYYY-NNNN"""
    year = datetime.now().year
    prefix = f"PO-{year}-"

    # Get last PO for current year
    last_po = PurchaseOrder.objects.filter(
        po_number__startswith=prefix
    ).order_by('-po_number').first()

    if last_po:
        # Extract number and increment
        last_number = int(last_po.po_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"


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
