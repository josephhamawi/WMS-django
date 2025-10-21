from django.urls import path
from . import views, request_views, auth_views, procurement_views, issuance_views, transfer_views

urlpatterns = [
    # Authentication
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Inventory & Warehouse Operations Dashboard
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),

    # Inventory Management
    path('inventory/products/', views.inventory_list, name='inventory_list'),
    path('inventory/products/add/', views.add_inventory, name='add_inventory'),
    path('inventory/products/update/<int:product_id>/', views.update_inventory, name='update_inventory'),

    # Item Request Management
    path('requests/', request_views.request_list, name='request_list'),
    path('requests/add/', request_views.request_add, name='request_add'),
    path('requests/<int:request_id>/', request_views.request_detail, name='request_detail'),
    path('requests/<int:request_id>/edit/', request_views.request_edit, name='request_edit'),
    path('requests/<int:request_id>/delete/', request_views.request_delete, name='request_delete'),
    path('requests/<int:request_id>/approve/', request_views.request_approve, name='request_approve'),
    path('requests/<int:request_id>/reject/', request_views.request_reject, name='request_reject'),

    # Procurement Management
    path('procurement/', procurement_views.procurement_dashboard, name='procurement_dashboard'),

    # Vendor Management
    path('procurement/vendors/', procurement_views.vendor_list, name='vendor_list'),
    path('procurement/vendors/add/', procurement_views.vendor_add, name='vendor_add'),
    path('procurement/vendors/update/<int:vendor_id>/', procurement_views.vendor_update, name='vendor_update'),
    path('procurement/vendors/delete/<int:vendor_id>/', procurement_views.vendor_delete, name='vendor_delete'),

    # Purchase Orders
    path('procurement/po/', procurement_views.po_list, name='po_list'),
    path('procurement/po/add/', procurement_views.po_add, name='po_add'),
    path('procurement/po/<int:po_id>/', procurement_views.po_detail, name='po_detail'),
    path('procurement/po/<int:po_id>/edit/', procurement_views.po_edit, name='po_edit'),
    path('procurement/po/<int:po_id>/delete/', procurement_views.po_delete, name='po_delete'),
    path('procurement/po/<int:po_id>/change-status/', procurement_views.po_change_status, name='po_change_status'),

    # Quotations
    path('procurement/quotations/', procurement_views.quotation_list, name='quotation_list'),
    path('procurement/quotations/add/', procurement_views.quotation_add, name='quotation_add'),
    path('procurement/quotations/<int:quotation_id>/', procurement_views.quotation_detail, name='quotation_detail'),
    path('procurement/quotations/<int:quotation_id>/edit/', procurement_views.quotation_edit, name='quotation_edit'),
    path('procurement/quotations/<int:quotation_id>/delete/', procurement_views.quotation_delete, name='quotation_delete'),
    path('procurement/quotations/<int:quotation_id>/convert-to-po/', procurement_views.quotation_to_po, name='quotation_to_po'),

    # Issuance Management
    path('issuance/', issuance_views.issuance_list, name='issuance_list'),
    path('issuance/create/', issuance_views.issuance_create, name='issuance_create'),
    path('issuance/<int:issuance_id>/', issuance_views.issuance_detail, name='issuance_detail'),
    path('issuance/request-items/<int:request_id>/', issuance_views.get_request_items, name='get_request_items'),

    # Transfer Management
    path('transfer/', transfer_views.transfer_list, name='transfer_list'),
    path('transfer/create/', transfer_views.transfer_create, name='transfer_create'),
    path('transfer/<int:transfer_id>/', transfer_views.transfer_detail, name='transfer_detail'),
    path('transfer/<int:transfer_id>/complete/', transfer_views.transfer_complete, name='transfer_complete'),
    path('transfer/<int:transfer_id>/cancel/', transfer_views.transfer_cancel, name='transfer_cancel'),
]
