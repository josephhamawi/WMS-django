from django.contrib import admin
from .models import (
    UnitOfMeasure, StorageLocation, Product, Department, Site, Team, UserProfile,
    Currency, Vendor, VendorProduct,
    PurchaseOrder, PurchaseOrderItem, Quotation, QuotationItem,
    Receiving, ReceivingItem,
    ItemRequest, ItemRequestLine, ItemIssuance, ItemIssuanceLine
)


# ==================== Inline Admin Classes ====================

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['product', 'quantity_ordered', 'quantity_received', 'unit_price']


class ReceivingItemInline(admin.TabularInline):
    model = ReceivingItem
    extra = 1
    fields = ['po_item', 'quantity_received', 'condition_notes']


class ItemRequestLineInline(admin.TabularInline):
    model = ItemRequestLine
    extra = 1
    fields = ['product', 'quantity_requested', 'destination_site', 'remarks', 'quantity_approved', 'quantity_issued']


class ItemIssuanceLineInline(admin.TabularInline):
    model = ItemIssuanceLine
    extra = 1
    fields = ['request_line', 'quantity_issued']


class VendorProductInline(admin.TabularInline):
    model = VendorProduct
    extra = 1
    fields = ['product', 'vendor_sku', 'unit_price', 'currency', 'minimum_order_quantity', 'lead_time_days', 'is_active']


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'vendor_sku', 'lead_time_days', 'notes']


# ==================== Model Admin Classes ====================

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'abbreviation']
    list_editable = ['is_active']


@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name', 'description']
    list_editable = ['is_active']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'manager', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    list_editable = ['is_active']


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_person', 'contact_phone', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name', 'address']
    list_editable = ['is_active']
    fieldsets = (
        ('Site Information', {
            'fields': ('code', 'name', 'address')
        }),
        ('Contact Details', {
            'fields': ('contact_person', 'contact_phone')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )
    readonly_fields = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'unit_of_measure', 'quantity', 'min_quantity', 'is_low_stock', 'location', 'unit_price', 'created_at']
    list_filter = ['location', 'unit_of_measure', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'description', 'unit_of_measure')
        }),
        ('Stock Information', {
            'fields': ('quantity', 'min_quantity', 'location', 'unit_price')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['name', 'description']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'team', 'employee_id', 'is_approved']
    list_filter = ['role', 'department', 'team', 'is_approved']
    search_fields = ['user__username', 'user__email', 'employee_id']
    list_editable = ['is_approved']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id', 'phone')
        }),
        ('Organization', {
            'fields': ('department', 'team', 'role')
        }),
        ('Account Status', {
            'fields': ('is_approved',)
        }),
    )


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'external_po_number', 'supplier_name', 'status', 'order_date', 'expected_delivery', 'total_amount', 'created_by']
    list_filter = ['status', 'order_date', 'created_at']
    search_fields = ['po_number', 'external_po_number', 'supplier_name']
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    inlines = [PurchaseOrderItemInline]
    fieldsets = (
        ('PO Information', {
            'fields': ('po_number', 'external_po_number', 'supplier_name', 'supplier_contact', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_delivery')
        }),
        ('Details', {
            'fields': ('notes', 'created_by', 'total_amount')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Receiving)
class ReceivingAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'received_date', 'received_by', 'status']
    list_filter = ['status', 'received_date']
    search_fields = ['purchase_order__po_number']
    inlines = [ReceivingItemInline]


@admin.register(ItemRequest)
class ItemRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'requested_by', 'department', 'priority', 'status', 'requested_date', 'approved_by']
    list_filter = ['status', 'priority', 'department', 'requested_date']
    search_fields = ['request_number', 'requested_by__username', 'department__name', 'department__code']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ItemRequestLineInline]
    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'requested_by', 'department', 'priority', 'status')
        }),
        ('Purpose & Details', {
            'fields': ('purpose', 'requested_date', 'required_by_date')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_date', 'rejection_reason')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemIssuance)
class ItemIssuanceAdmin(admin.ModelAdmin):
    list_display = ['issue_number', 'item_request', 'issued_to', 'issued_by', 'issued_date', 'status']
    list_filter = ['status', 'issued_date']
    search_fields = ['issue_number', 'item_request__request_number']
    inlines = [ItemIssuanceLineInline]


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    list_editable = ['is_active']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_person', 'email', 'phone', 'currency', 'is_active']
    list_filter = ['is_active', 'currency']
    search_fields = ['code', 'name', 'email', 'contact_person']
    list_editable = ['is_active']
    inlines = [VendorProductInline]
    fieldsets = (
        ('Vendor Information', {
            'fields': ('code', 'name', 'currency')
        }),
        ('Contact Details', {
            'fields': ('contact_person', 'email', 'phone', 'address')
        }),
        ('Payment Terms', {
            'fields': ('payment_terms',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(VendorProduct)
class VendorProductAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'product', 'unit_price', 'currency', 'minimum_order_quantity', 'lead_time_days', 'is_active']
    list_filter = ['vendor', 'currency', 'is_active']
    search_fields = ['vendor__name', 'product__name', 'vendor_sku']
    list_editable = ['unit_price', 'is_active']


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'vendor', 'status', 'request_date', 'valid_until', 'total_amount', 'created_by']
    list_filter = ['status', 'vendor', 'request_date']
    search_fields = ['quotation_number', 'vendor__name']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [QuotationItemInline]
    fieldsets = (
        ('Quotation Information', {
            'fields': ('quotation_number', 'vendor', 'currency', 'status')
        }),
        ('Dates', {
            'fields': ('request_date', 'quotation_date', 'valid_until')
        }),
        ('Details', {
            'fields': ('notes', 'created_by', 'total_amount')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Customize admin site header
admin.site.site_header = "Warehouse Management System"
admin.site.site_title = "WMS Admin"
admin.site.index_title = "Welcome to Warehouse Management System"
