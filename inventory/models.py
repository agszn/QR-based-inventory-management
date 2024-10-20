# models.py
from django.db import models

class Item(models.Model):
    ITEM_CLASSES = (
        ('electronic', 'Electronic'),
        ('chemical', 'Chemical'),
        ('books', 'Books'),
        ('clothing', 'Clothing'),
        ('food', 'Food'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=100)
    units = models.IntegerField()
    fragile = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    unit_choices = models.CharField(max_length=20, choices=(('grams', 'grams'), ('kilos', 'kilos'), ('tonnes', 'tonnes')))
    item_class = models.CharField(max_length=20, choices=ITEM_CLASSES)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    units = models.IntegerField(default=0)
    fragile = models.BooleanField(default=False)
    weight = models.FloatField(default=0)
    unit = models.CharField(max_length=50)
    item_class = models.CharField(max_length=50)

    def __str__(self):
        return self.name

from django.utils import timezone

class scannedItems(models.Model):
    name = models.CharField(max_length=100)
    units = models.IntegerField(default=0)
    fragile = models.BooleanField(default=False)
    weight = models.FloatField(default=0)
    unit = models.CharField(max_length=50)
    item_class = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
