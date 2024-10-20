
# forms.py
from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'units', 'fragile', 'weight', 'unit_choices', 'item_class']

from .models import scannedItems

class ScannedItemForm(forms.ModelForm):
    class Meta:
        model = scannedItems
        fields = ['name', 'units', 'fragile', 'weight', 'unit', 'item_class']
