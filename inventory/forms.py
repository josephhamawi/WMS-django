"""
Forms for inventory management
"""
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    ItemRequest, ItemRequestLine, PurchaseOrder, PurchaseOrderItem,
    Product, Department, Site
)


class ItemRequestForm(forms.ModelForm):
    """Form for Item Request header"""

    class Meta:
        model = ItemRequest
        fields = ['requested_by', 'department', 'priority', 'purpose',
                  'requested_date', 'required_by_date']
        widgets = {
            'requested_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'required_by_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'requested_by': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ItemRequestLineForm(forms.ModelForm):
    """Form for Item Request line items"""

    class Meta:
        model = ItemRequestLine
        fields = ['product', 'quantity_requested', 'destination_site', 'remarks']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'destination_site': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks'}),
        }


# Formset for multiple line items
ItemRequestLineFormSet = inlineformset_factory(
    ItemRequest,
    ItemRequestLine,
    form=ItemRequestLineForm,
    extra=1,  # Start with 1 empty row
    can_delete=True,
    min_num=1,  # Require at least 1 line
    validate_min=True,
)


class PurchaseOrderForm(forms.ModelForm):
    """Form for Purchase Order header"""

    class Meta:
        model = PurchaseOrder
        fields = ['supplier_name', 'supplier_contact', 'status',
                  'order_date', 'expected_delivery', 'notes']
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expected_delivery': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    """Form for Purchase Order line items"""

    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity_ordered', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity_ordered': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # New users are just regular users, not staff
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user
