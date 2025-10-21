from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ==================== Core Inventory Models ====================

class UnitOfMeasure(models.Model):
    """Unit of Measure for products (e.g., Pieces, Kg, Liters, Boxes)"""
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

    class Meta:
        ordering = ['name']
        verbose_name = "Unit of Measure"
        verbose_name_plural = "Units of Measure"


class StorageLocation(models.Model):
    """Storage locations within the warehouse (e.g., Shelf A1, Zone B, Room 5)"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Location code (e.g., A1, B2, ZONE-1)")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']
        verbose_name = "Storage Location"
        verbose_name_plural = "Storage Locations"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.IntegerField(default=0)
    min_quantity = models.IntegerField(default=10, help_text="Minimum stock level")
    location = models.ForeignKey('StorageLocation', on_delete=models.PROTECT, related_name='products', null=True, blank=True, help_text="Warehouse storage location")
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    unit_of_measure = models.ForeignKey('UnitOfMeasure', on_delete=models.PROTECT, related_name='products', null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='products_created')

    def __str__(self):
        uom_display = f" ({self.unit_of_measure.abbreviation})" if self.unit_of_measure else ""
        return f"{self.name}{uom_display} [SKU: {self.sku}]"

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity

    class Meta:
        permissions = [
            ('view_inventory', 'Can view inventory'),
            ('add_inventory', 'Can add inventory'),
            ('update_inventory', 'Can update inventory'),
            ('delete_inventory', 'Can delete inventory'),
        ]
        ordering = ['-created_at']


# ==================== Organization Structure ====================

class Department(models.Model):
    """Departments within the organization"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Department code (e.g., IT, HR, OPS)")
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


class Site(models.Model):
    """Physical sites/locations where items can be delivered"""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Warehouse Manager'),
        ('staff', 'Warehouse Staff'),
        ('requester', 'Item Requester'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=20, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_approved = models.BooleanField(default=False, help_text="Account approval status")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"


# ==================== Supplier/Vendor Management ====================

class Currency(models.Model):
    """Currency for pricing and transactions"""
    code = models.CharField(max_length=3, unique=True, help_text="ISO currency code (USD, EUR, etc.)")
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.symbol})"

    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ['code']


class Vendor(models.Model):
    """Suppliers/Vendors for purchasing"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Vendor code")
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    payment_terms = models.CharField(max_length=255, blank=True, help_text="e.g., Net 30, Net 60")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='vendors', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']


class VendorProduct(models.Model):
    """Product pricing from specific vendors"""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='vendor_prices')
    vendor_sku = models.CharField(max_length=100, blank=True, help_text="Vendor's product code")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='vendor_prices')
    minimum_order_quantity = models.IntegerField(default=1)
    lead_time_days = models.IntegerField(default=0, help_text="Delivery lead time in days")
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.product.name}: {self.currency.symbol}{self.unit_price}"

    class Meta:
        unique_together = ['vendor', 'product']
        verbose_name = "Vendor Product Pricing"
        verbose_name_plural = "Vendor Product Pricing"


# ==================== Purchase Order Management ====================

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('partially_received', 'Partially Received'),
        ('received', 'Fully Received'),
        ('cancelled', 'Cancelled'),
    ]

    po_number = models.CharField(max_length=100, unique=True, help_text="Internal PO number (auto-generated)")
    external_po_number = models.CharField(max_length=100, blank=True, help_text="External/Reference PO number from another system")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders', null=True, blank=True)
    # Keep legacy fields for compatibility
    supplier_name = models.CharField(max_length=255, blank=True, help_text="Legacy field - use vendor instead")
    supplier_contact = models.CharField(max_length=255, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='purchase_orders', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField(default=timezone.now)
    expected_delivery = models.DateField(null=True, blank=True)
    delivery_address = models.TextField(blank=True, help_text="Delivery address if different from default")
    payment_terms = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pos_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pos_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        vendor_name = self.vendor.name if self.vendor else self.supplier_name
        return f"PO-{self.po_number} - {vendor_name}"

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def display_vendor(self):
        """Get vendor name from vendor object or legacy field"""
        return self.vendor.name if self.vendor else self.supplier_name

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"


class Quotation(models.Model):
    """Vendor quotations for purchase orders"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent to Vendor'),
        ('received', 'Quotation Received'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    quotation_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='quotations')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='quotations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    request_date = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True)
    quotation_date = models.DateField(null=True, blank=True, help_text="Date vendor provided quotation")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='quotations_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QTN-{self.quotation_number} - {self.vendor.name}"

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    class Meta:
        ordering = ['-created_at']


class QuotationItem(models.Model):
    """Line items in a quotation"""
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quotation_items')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    vendor_sku = models.CharField(max_length=100, blank=True, help_text="Vendor's product code")
    lead_time_days = models.IntegerField(default=0, help_text="Delivery lead time in days")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} - Qty: {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    class Meta:
        verbose_name = "Quotation Item"
        verbose_name_plural = "Quotation Items"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='po_items')
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - Qty: {self.quantity_ordered}"

    @property
    def total_price(self):
        return self.quantity_ordered * self.unit_price

    @property
    def quantity_remaining(self):
        return self.quantity_ordered - self.quantity_received


# ==================== Receiving Management ====================

class Receiving(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('partial', 'Partial'),
    ]

    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='receivings')
    received_date = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='receivings_processed')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receiving for {self.purchase_order.po_number} on {self.received_date.date()}"

    class Meta:
        ordering = ['-received_date']


class ReceivingItem(models.Model):
    receiving = models.ForeignKey(Receiving, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name='received_items')
    quantity_received = models.IntegerField()
    condition_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.po_item.product.name} - Received: {self.quantity_received}"


# ==================== Item Request & Issuance ====================

class ItemRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('issued', 'Issued'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    request_number = models.CharField(max_length=100, unique=True)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_requests')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='item_requests')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    purpose = models.TextField(help_text="Purpose/Remarks for this request")
    requested_date = models.DateTimeField(default=timezone.now)
    required_by_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if applicable")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        dept_display = f" ({self.department.code})" if self.department else ""
        return f"REQ-{self.request_number}{dept_display} - {self.requested_by.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Item Request"
        verbose_name_plural = "Item Requests"


class ItemRequestLine(models.Model):
    item_request = models.ForeignKey(ItemRequest, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='request_lines')
    quantity_requested = models.IntegerField()
    quantity_approved = models.IntegerField(default=0)
    quantity_issued = models.IntegerField(default=0)
    destination_site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='requested_items', help_text="Site where item will be delivered")
    remarks = models.TextField(blank=True, help_text="Specific remarks for this item")

    def __str__(self):
        site_display = f" → {self.destination_site.code}" if self.destination_site else ""
        return f"{self.product.name} - Qty: {self.quantity_requested}{site_display}"

    @property
    def quantity_remaining(self):
        return self.quantity_approved - self.quantity_issued

    class Meta:
        verbose_name = "Item Request Line"
        verbose_name_plural = "Item Request Lines"


class ItemIssuance(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    item_request = models.ForeignKey(ItemRequest, on_delete=models.CASCADE, related_name='issuances')
    issue_number = models.CharField(max_length=100, unique=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issuances_processed')
    issued_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items_received')
    issued_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ISS-{self.issue_number} for REQ-{self.item_request.request_number}"

    class Meta:
        ordering = ['-issued_date']


class ItemIssuanceLine(models.Model):
    issuance = models.ForeignKey(ItemIssuance, on_delete=models.CASCADE, related_name='lines')
    request_line = models.ForeignKey(ItemRequestLine, on_delete=models.CASCADE, related_name='issuance_lines')
    quantity_issued = models.IntegerField()

    def __str__(self):
        return f"{self.request_line.product.name} - Issued: {self.quantity_issued}"


# ==================== Transfer Management ====================

class Transfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    transfer_number = models.CharField(max_length=100, unique=True, help_text="Transfer number (auto-generated)")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='transfers')
    quantity = models.IntegerField(help_text="Quantity to transfer")
    from_location = models.ForeignKey(StorageLocation, on_delete=models.PROTECT, related_name='transfers_from', help_text="Source location")
    to_location = models.ForeignKey(StorageLocation, on_delete=models.PROTECT, related_name='transfers_to', help_text="Destination location")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_requested')
    transferred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_processed')
    transfer_date = models.DateTimeField(null=True, blank=True, help_text="Date when transfer was completed")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TRF-{self.transfer_number} - {self.product.name} ({self.from_location.code} → {self.to_location.code})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"
