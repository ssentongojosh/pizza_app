from django.db import models

# Create your models here.

class MenuItem(models.Model):
    """Pizza menu item model."""
    CATEGORY_CHOICES = [
        ('PIZZA', 'Pizza'),
        ('APPETIZER', 'Appetizer'),
        ('DRINK', 'Drink'),
        ('DESSERT', 'Dessert'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    #image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='PIZZA')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['category', 'name']