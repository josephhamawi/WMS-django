from django.urls import path
from . import views, request_views, auth_views, procurement_views, issuance_views

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
    path('procurement/vendors/', procurement_views.vendor_list, name='vendor_list'),
    path('procurement/po/', procurement_views.po_list, name='po_list'),
    path('procurement/quotations/', procurement_views.quotation_list, name='quotation_list'),

    # Issuance Management
    path('issuance/', issuance_views.issuance_list, name='issuance_list'),
    path('issuance/create/', issuance_views.issuance_create, name='issuance_create'),
    path('issuance/<int:issuance_id>/', issuance_views.issuance_detail, name='issuance_detail'),
    path('issuance/request-items/<int:request_id>/', issuance_views.get_request_items, name='get_request_items'),
]
