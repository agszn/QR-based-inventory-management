from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Consumer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Student Name")
    email = models.EmailField(max_length=277, verbose_name="Student Email")
    image = models.ImageField(upload_to='consumer_images/', null=True, blank=True, verbose_name="Consumer Image")
    content = models.TextField(verbose_name="Consumer Content", blank=True, null=True)

    def __str__(self):
        return str(self.id)

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name


class Review(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f'Review for {self.consumer.name}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"



# 
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