# Pizza Ordering Django Web Application
# Complete implementation with all required features

# requirements.txt
"""
Django>=5.0,<6.0
stripe>=5.0.0
pillow>=9.0.0
"""

# pizza_project/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'menu',
    'orders',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pizza_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pizza_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Stripe settings
STRIPE_PUBLIC_KEY = 'pk_test_...'  # Replace with your test key
STRIPE_SECRET_KEY = 'sk_test_...'  # Replace with your test key

# pizza_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('', lambda request: redirect('menu:menu_list')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    address = models.CharField("Delivery Address", max_length=255, blank=True)
    phone = models.CharField("Phone Number", max_length=20, blank=True)
    
    def __str__(self):
        return self.username

# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=255, required=False)
    phone = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = CustomUser
        fields = ("username", "email", "address", "phone", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.address = self.cleaned_data["address"]
        user.phone = self.cleaned_data["phone"]
        if commit:
            user.save()
        return user

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import CustomUserCreationForm

def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('menu:menu_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/menu/'

@login_required
def profile_view(request):
    """User profile view."""
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.address = request.POST.get('address', user.address)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        messages.success(request, 'Profile updated successfully!')
    return render(request, 'accounts/profile.html', {'user': request.user})

def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('menu:menu_list')

# accounts/urls.py
from django.urls import path
from .views import register_view, CustomLoginView, logout_view, profile_view

app_name = 'accounts'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
]

# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('address', 'phone')}),
    )

# menu/models.py
from django.db import models

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
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='PIZZA')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['category', 'name']

# menu/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import MenuItem

def menu_list(request):
    """Display all available menu items."""
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    items = MenuItem.objects.filter(is_available=True)
    
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if category:
        items = items.filter(category=category)
    
    categories = MenuItem.CATEGORY_CHOICES
    
    context = {
        'items': items,
        'categories': categories,
        'current_search': search_query,
        'current_category': category,
    }
    return render(request, 'menu/menu_list.html', context)

def menu_detail(request, pk):
    """Display detailed view of a menu item."""
    item = get_object_or_404(MenuItem, pk=pk, is_available=True)
    return render(request, 'menu/menu_detail.html', {'item': item})

# menu/urls.py
from django.urls import path
from .views import menu_list, menu_detail

app_name = 'menu'

urlpatterns = [
    path('', menu_list, name='menu_list'),
    path('item/<int:pk>/', menu_detail, name='menu_detail'),
]

# menu/admin.py
from django.contrib import admin
from .models import MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_available', 'price')

# orders/models.py
from django.db import models
from django.conf import settings
from menu.models import MenuItem
import uuid

class Order(models.Model):
    """Customer order model."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def calculate_total(self):
        """Calculate total amount for the order."""
        return sum(item.get_total() for item in self.items.all())
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    """Individual items in an order."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Price at order time
    
    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
    
    def get_total(self):
        """Get total price for this order item."""
        return self.price * self.quantity

# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from menu.models import MenuItem
from .models import Order, OrderItem
import json

def add_to_cart(request, item_id):
    """Add a MenuItem to the shopping cart."""
    item = get_object_or_404(MenuItem, pk=item_id, is_available=True)
    cart = request.session.get('cart', {})
    
    cart[str(item_id)] = {
        'quantity': cart.get(str(item_id), {}).get('quantity', 0) + 1,
        'name': item.name,
        'price': str(item.price)
    }
    
    request.session['cart'] = cart
    messages.success(request, f'{item.name} added to cart!')
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({'success': True, 'cart_count': len(cart)})
    
    return redirect('orders:cart_detail')

def remove_from_cart(request, item_id):
    """Remove a MenuItem from the shopping cart."""
    cart = request.session.get('cart', {})
    
    if str(item_id) in cart:
        item_name = cart[str(item_id)]['name']
        del cart[str(item_id)]
        request.session['cart'] = cart
        messages.success(request, f'{item_name} removed from cart!')
    
    return redirect('orders:cart_detail')

def update_cart_quantity(request, item_id):
    """Update quantity of an item in cart."""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        
        if str(item_id) in cart and quantity > 0:
            cart[str(item_id)]['quantity'] = quantity
            request.session['cart'] = cart
            messages.success(request, 'Cart updated!')
        elif quantity <= 0:
            return remove_from_cart(request, item_id)
    
    return redirect('orders:cart_detail')

def cart_detail(request):
    """Display cart summary and total."""
    cart = request.session.get('cart', {})
    items = []
    total = 0
    
    for item_id, cart_item in cart.items():
        try:
            menu_item = MenuItem.objects.get(pk=int(item_id), is_available=True)
            item_total = menu_item.price * cart_item['quantity']
            items.append({
                'menu_item': menu_item,
                'quantity': cart_item['quantity'],
                'total': item_total
            })
            total += item_total
        except MenuItem.DoesNotExist:
            # Remove invalid items from cart
            continue
    
    context = {
        'items': items,
        'total': total,
        'cart_count': len(cart)
    }
    return render(request, 'orders/cart.html', context)

def checkout(request):
    """Checkout process."""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Your cart is empty!')
        return redirect('menu:menu_list')
    
    # Calculate total
    total = 0
    cart_items = []
    
    for item_id, cart_item in cart.items():
        try:
            menu_item = MenuItem.objects.get(pk=int(item_id), is_available=True)
            item_total = menu_item.price * cart_item['quantity']
            cart_items.append({
                'menu_item': menu_item,
                'quantity': cart_item['quantity'],
                'total': item_total
            })
            total += item_total
        except MenuItem.DoesNotExist:
            continue
    
    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            delivery_address=request.POST.get('delivery_address'),
            total_amount=total
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item['menu_item'],
                quantity=cart_item['quantity'],
                price=cart_item['menu_item'].price
            )
        
        # Store order ID in session for payment
        request.session['pending_order_id'] = order.id
        
        # Redirect to payment
        return redirect('payments:process_payment')
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'user': request.user if request.user.is_authenticated else None
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_list(request):
    """Display user's order history."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__menu_item')
    return render(request, 'orders/order_list.html', {'orders': orders})

def order_detail(request, order_number):
    """Display order details."""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Allow access if user owns the order or provide order number
    if request.user.is_authenticated and order.user == request.user:
        pass  # User owns the order
    elif not request.user.is_authenticated:
        # For guest orders, you might want additional verification
        pass
    else:
        messages.error(request, 'Order not found.')
        return redirect('menu:menu_list')
    
    return render(request, 'orders/order_detail.html', {'order': order})

# orders/urls.py
from django.urls import path
from .views import (
    add_to_cart, remove_from_cart, update_cart_quantity,
    cart_detail, checkout, order_list, order_detail
)

app_name = 'orders'

urlpatterns = [
    path('add/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', update_cart_quantity, name='update_cart_quantity'),
    path('cart/', cart_detail, name='cart_detail'),
    path('checkout/', checkout, name='checkout'),
    path('my-orders/', order_list, name='order_list'),
    path('order/<str:order_number>/', order_detail, name='order_detail'),
]

# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total',)
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'email', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'email', 'user__username')
    list_editable = ('status',)
    readonly_fields = ('order_number', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Recalculate total when order is saved
        obj.total_amount = obj.calculate_total()
        obj.save()

# payments/models.py
from django.db import models
from django.conf import settings
from orders.models import Order

class Payment(models.Model):
    """Payment record model."""
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for Order {self.order.order_number} - ${self.amount}"

# payments/views.py
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from orders.models import Order
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def process_payment(request):
    """Process payment for pending order."""
    order_id = request.session.get('pending_order_id')
    
    if not order_id:
        messages.error(request, 'No pending order found.')
        return redirect('menu:menu_list')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        try:
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Pizza Order #{order.order_number}',
                        },
                        'unit_amount': int(order.total_amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payments/success/'),
                cancel_url=request.build_absolute_uri('/orders/cart/'),
                metadata={
                    'order_id': order.id,
                    'order_number': order.order_number,
                }
            )
            
            # Create payment record
            Payment.objects.create(
                order=order,
                stripe_payment_intent_id=checkout_session.payment_intent,
                amount=order.total_amount,
                status='PENDING'
            )
            
            return redirect(checkout_session.url)
            
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('orders:checkout')
    
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'payments/process_payment.html', context)

def payment_success(request):
    """Handle successful payment."""
    order_id = request.session.get('pending_order_id')
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'CONFIRMED'
            order.save()
            
            # Update payment status
            if hasattr(order, 'payment'):
                order.payment.status = 'COMPLETED'
                order.payment.save()
            
            # Clear cart and order from session
            request.session.pop('cart', None)
            request.session.pop('pending_order_id', None)
            
            context = {'order': order}
            return render(request, 'payments/payment_success.html', context)
            
        except Order.DoesNotExist:
            pass
    
    messages.error(request, 'Payment verification failed.')
    return redirect('menu:menu_list')

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_ENDPOINT_SECRET', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle payment_intent.succeeded event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Update payment status in database
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'COMPLETED'
            payment.save()
            
            # Update order status
            payment.order.status = 'CONFIRMED'
            payment.order.save()
        except Payment.DoesNotExist:
            pass
    
    return JsonResponse({'success': True})

# payments/urls.py
from django.urls import path
from .views import process_payment, payment_success, stripe_webhook

app_name = 'payments'

urlpatterns = [
    path('process/', process_payment, name='process_payment'),
    path('success/', payment_success, name='payment_success'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]

# payments/admin.py
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'stripe_payment_intent_id')
    readonly_fields = ('created_at', 'updated_at')

# templates/orders/checkout.html
"""
{% extends 'base.html' %}

{% block title %}Checkout - Pizza Palace{% endblock %}

{% block content %}
<h2>Checkout</h2>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Delivery Information</h5>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="email" class="form-label">Email *</label>
                            <input type="email" class="form-control" id="email" name="email" 
                                   value="{% if user.is_authenticated %}{{ user.email }}{% endif %}" required>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label for="phone" class="form-label">Phone Number *</label>
                            <input type="tel" class="form-control" id="phone" name="phone" 
                                   value="{% if user.is_authenticated %}{{ user.phone }}{% endif %}" required>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="delivery_address" class="form-label">Delivery Address *</label>
                        <textarea class="form-control" id="delivery_address" name="delivery_address" 
                                  rows="3" required>{% if user.is_authenticated %}{{ user.address }}{% endif %}</textarea>
                    </div>
                    
                    <button type="submit" class="btn btn-danger btn-lg w-100">
                        <i class="fas fa-credit-card"></i> Proceed to Payment
                    </button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Order Summary</h5>
            </div>
            <div class="card-body">
                {% for item in cart_items %}
                    <div class="d-flex justify-content-between mb-2">
                        <div>
                            <strong>{{ item.menu_item.name }}</strong><br>
                            <small class="text-muted">Qty: {{ item.quantity }}</small>
                        </div>
                        <span>${{ item.total }}</span>
                    </div>
                {% endfor %}
                
                <hr>
                <div class="d-flex justify-content-between">
                    <strong>Total:</strong>
                    <strong class="text-danger">${{ total }}</strong>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# templates/orders/order_list.html
"""
{% extends 'base.html' %}

{% block title %}My Orders - Pizza Palace{% endblock %}

{% block content %}
<h2>My Orders</h2>

{% if orders %}
    {% for order in orders %}
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="mb-0">Order #{{ order.order_number }}</h5>
                    <small class="text-muted">{{ order.created_at|date:"M d, Y - g:i A" }}</small>
                </div>
                <div>
                    <span class="badge 
                        {% if order.status == 'PENDING' %}bg-warning
                        {% elif order.status == 'CONFIRMED' %}bg-info
                        {% elif order.status == 'PREPARING' %}bg-primary
                        {% elif order.status == 'OUT_FOR_DELIVERY' %}bg-secondary
                        {% elif order.status == 'DELIVERED' %}bg-success
                        {% elif order.status == 'CANCELLED' %}bg-danger
                        {% endif %}">
                        {{ order.get_status_display }}
                    </span>
                </div>
            </div>
            
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h6>Items:</h6>
                        {% for item in order.items.all %}
                            <div class="d-flex justify-content-between">
                                <span>{{ item.menu_item.name }} x {{ item.quantity }}</span>
                                <span>${{ item.get_total }}</span>
                            </div>
                        {% endfor %}
                    </div>
                    
                    <div class="col-md-4 text-end">
                        <h6>Total: <span class="text-danger">${{ order.total_amount }}</span></h6>
                        <a href="{% url 'orders:order_detail' order.order_number %}" class="btn btn-outline-danger btn-sm">
                            View Details
                        </a>
                    </div>
                </div>
            </div>
        </div>
    {% endfor %}
{% else %}
    <div class="text-center py-5">
        <i class="fas fa-receipt fa-5x text-muted mb-3"></i>
        <h3>No orders yet</h3>
        <p class="text-muted">Start by ordering some delicious pizza!</p>
        <a href="{% url 'menu:menu_list' %}" class="btn btn-danger">Browse Menu</a>
    </div>
{% endif %}
{% endblock %}
"""

# templates/orders/order_detail.html
"""
{% extends 'base.html' %}

{% block title %}Order #{{ order.order_number }} - Pizza Palace{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Order #{{ order.order_number }}</h5>
                <span class="badge 
                    {% if order.status == 'PENDING' %}bg-warning
                    {% elif order.status == 'CONFIRMED' %}bg-info
                    {% elif order.status == 'PREPARING' %}bg-primary
                    {% elif order.status == 'OUT_FOR_DELIVERY' %}bg-secondary
                    {% elif order.status == 'DELIVERED' %}bg-success
                    {% elif order.status == 'CANCELLED' %}bg-danger
                    {% endif %}">
                    {{ order.get_status_display }}
                </span>
            </div>
            
            <div class="card-body">
                <div class="row mb-4">
                    <div class="col-md-6">
                        <h6>Order Details</h6>
                        <p><strong>Order Date:</strong> {{ order.created_at|date:"M d, Y - g:i A" }}</p>
                        <p><strong>Status:</strong> {{ order.get_status_display }}</p>
                        {% if order.user %}
                            <p><strong>Customer:</strong> {{ order.user.username }}</p>
                        {% endif %}
                    </div>
                    
                    <div class="col-md-6">
                        <h6>Delivery Information</h6>
                        <p><strong>Email:</strong> {{ order.email }}</p>
                        <p><strong>Phone:</strong> {{ order.phone }}</p>
                        <p><strong>Address:</strong><br>{{ order.delivery_address|linebreaks }}</p>
                    </div>
                </div>
                
                <h6>Order Items</h6>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in order.items.all %}
                                <tr>
                                    <td>{{ item.menu_item.name }}</td>
                                    <td>${{ item.price }}</td>
                                    <td>{{ item.quantity }}</td>
                                    <td>${{ item.get_total }}</td>
                                </tr>
                            {% endfor %}
                        </tbody>
                        <tfoot>
                            <tr>
                                <th colspan="3">Total:</th>
                                <th class="text-danger">${{ order.total_amount }}</th>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0">Order Tracking</h6>
            </div>
            <div class="card-body">
                <div class="timeline">
                    <div class="timeline-item {% if order.status == 'PENDING' or order.status == 'CONFIRMED' or order.status == 'PREPARING' or order.status == 'OUT_FOR_DELIVERY' or order.status == 'DELIVERED' %}active{% endif %}">
                        <i class="fas fa-check-circle"></i>
                        <span>Order Placed</span>
                    </div>
                    
                    <div class="timeline-item {% if order.status == 'CONFIRMED' or order.status == 'PREPARING' or order.status == 'OUT_FOR_DELIVERY' or order.status == 'DELIVERED' %}active{% endif %}">
                        <i class="fas fa-credit-card"></i>
                        <span>Payment Confirmed</span>
                    </div>
                    
                    <div class="timeline-item {% if order.status == 'PREPARING' or order.status == 'OUT_FOR_DELIVERY' or order.status == 'DELIVERED' %}active{% endif %}">
                        <i class="fas fa-utensils"></i>
                        <span>Preparing Order</span>
                    </div>
                    
                    <div class="timeline-item {% if order.status == 'OUT_FOR_DELIVERY' or order.status == 'DELIVERED' %}active{% endif %}">
                        <i class="fas fa-truck"></i>
                        <span>Out for Delivery</span>
                    </div>
                    
                    <div class="timeline-item {% if order.status == 'DELIVERED' %}active{% endif %}">
                        <i class="fas fa-home"></i>
                        <span>Delivered</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="mt-3">
    <a href="{% url 'orders:order_list' %}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-left"></i> Back to Orders
    </a>
</div>
{% endblock %}
"""

# templates/payments/process_payment.html
"""
{% extends 'base.html' %}

{% block title %}Payment - Pizza Palace{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Payment for Order #{{ order.order_number }}</h5>
            </div>
            <div class="card-body">
                <div class="mb-4">
                    <h6>Order Summary</h6>
                    {% for item in order.items.all %}
                        <div class="d-flex justify-content-between">
                            <span>{{ item.menu_item.name }} x {{ item.quantity }}</span>
                            <span>${{ item.get_total }}</span>
                        </div>
                    {% endfor %}
                    <hr>
                    <div class="d-flex justify-content-between">
                        <strong>Total:</strong>
                        <strong class="text-danger">${{ order.total_amount }}</strong>
                    </div>
                </div>
                
                <form method="post">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-danger btn-lg w-100">
                        <i class="fas fa-credit-card"></i> Pay with Stripe
                    </button>
                </form>
                
                <div class="text-center mt-3">
                    <small class="text-muted">
                        <i class="fas fa-lock"></i> Secure payment powered by Stripe
                    </small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# templates/payments/payment_success.html
"""
{% extends 'base.html' %}

{% block title %}Payment Success - Pizza Palace{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8 text-center">
        <div class="card">
            <div class="card-body py-5">
                <i class="fas fa-check-circle fa-5x text-success mb-4"></i>
                <h2 class="text-success">Payment Successful!</h2>
                <p class="lead">Thank you for your order!</p>
                
                <div class="card bg-light mx-auto" style="max-width: 400px;">
                    <div class="card-body">
                        
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Pizza Palace{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-danger">
        <div class="container">
            <a class="navbar-brand" href="{% url 'menu:menu_list' %}">
                <i class="fas fa-pizza-slice"></i> Pizza Palace
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'menu:menu_list' %}">Menu</a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'orders:cart_detail' %}">
                            <i class="fas fa-shopping-cart"></i> Cart
                            <span class="badge bg-light text-dark" id="cart-count">{{ request.session.cart|length }}</span>
                        </a>
                    </li>
                    
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'orders:order_list' %}">My Orders</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:profile' %}">Profile</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:logout' %}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:login' %}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:register' %}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Messages -->
    {% if messages %}
        <div class="container mt-3">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        </div>
    {% endif %}

    <!-- Main Content -->
    <main class="container my-4">
        {% block content %}
        {% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center">
            <p>&copy; 2025 Pizza Palace. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% load static %}
    <script src="{% static 'js/cart.js' %}"></script>
</body>
</html>
"""

# templates/accounts/register.html
"""
{% extends 'base.html' %}

{% block title %}Register - Pizza Palace{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3 class="mb-0">Create Account</h3>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
                        {{ form.username }}
                        {% if form.username.errors %}
                            <div class="text-danger">{{ form.username.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.email.id_for_label }}" class="form-label">Email</label>
                        {{ form.email }}
                        {% if form.email.errors %}
                            <div class="text-danger">{{ form.email.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.address.id_for_label }}" class="form-label">Delivery Address</label>
                        {{ form.address }}
                        {% if form.address.errors %}
                            <div class="text-danger">{{ form.address.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.phone.id_for_label }}" class="form-label">Phone Number</label>
                        {{ form.phone }}
                        {% if form.phone.errors %}
                            <div class="text-danger">{{ form.phone.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.password1.id_for_label }}" class="form-label">Password</label>
                        {{ form.password1 }}
                        {% if form.password1.errors %}
                            <div class="text-danger">{{ form.password1.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.password2.id_for_label }}" class="form-label">Confirm Password</label>
                        {{ form.password2 }}
                        {% if form.password2.errors %}
                            <div class="text-danger">{{ form.password2.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <button type="submit" class="btn btn-danger w-100">Register</button>
                </form>
                
                <div class="text-center mt-3">
                    <p>Already have an account? <a href="{% url 'accounts:login' %}">Login here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# templates/accounts/login.html
"""
{% extends 'base.html' %}

{% block title %}Login - Pizza Palace{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3 class="mb-0">Login</h3>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
                        {{ form.username }}
                        {% if form.username.errors %}
                            <div class="text-danger">{{ form.username.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.password.id_for_label }}" class="form-label">Password</label>
                        {{ form.password }}
                        {% if form.password.errors %}
                            <div class="text-danger">{{ form.password.errors }}</div>
                        {% endif %}
                    </div>
                    
                    {% if form.non_field_errors %}
                        <div class="alert alert-danger">
                            {{ form.non_field_errors }}
                        </div>
                    {% endif %}
                    
                    <button type="submit" class="btn btn-danger w-100">Login</button>
                </form>
                
                <div class="text-center mt-3">
                    <p>Don't have an account? <a href="{% url 'accounts:register' %}">Register here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# templates/accounts/profile.html
"""
{% extends 'base.html' %}

{% block title %}Profile - Pizza Palace{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h3 class="mb-0">My Profile</h3>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-control" value="{{ user.username }}" readonly>
                    </div>
                    
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" value="{{ user.email }}">
                    </div>
                    
                    <div class="mb-3">
                        <label for="address" class="form-label">Delivery Address</label>
                        <textarea class="form-control" id="address" name="address" rows="3">{{ user.address }}</textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="phone" class="form-label">Phone Number</label>
                        <input type="text" class="form-control" id="phone" name="phone" value="{{ user.phone }}">
                    </div>
                    
                    <button type="submit" class="btn btn-danger">Update Profile</button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
                <a href="{% url 'orders:order_list' %}" class="btn btn-outline-danger w-100 mb-2">
                    <i class="fas fa-list"></i> View Orders
                </a>
                <a href="{% url 'menu:menu_list' %}" class="btn btn-outline-danger w-100">
                    <i class="fas fa-pizza-slice"></i> Order Now
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# templates/menu/menu_list.html
"""
{% extends 'base.html' %}

{% block title %}Menu - Pizza Palace{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-8">
        <h2>Our Menu</h2>
    </div>
    <div class="col-md-4">
        <form method="get" class="d-flex">
            <input type="text" name="search" class="form-control me-2" placeholder="Search menu..." value="{{ current_search }}">
            <button type="submit" class="btn btn-outline-danger">Search</button>
        </form>
    </div>
</div>

<!-- Category Filter -->
<div class="row mb-4">
    <div class="col-12">
        <div class="btn-group" role="group">
            <a href="{% url 'menu:menu_list' %}" class="btn btn-outline-danger {% if not current_category %}active{% endif %}">All</a>
            {% for code, name in categories %}
                <a href="{% url 'menu:menu_list' %}?category={{ code }}" 
                   class="btn btn-outline-danger {% if current_category == code %}active{% endif %}">{{ name }}</a>
            {% endfor %}
        </div>
    </div>
</div>

<!-- Menu Items -->
<div class="row">
    {% for item in items %}
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                {% if item.image %}
                    <img src="{{ item.image.url }}" class="card-img-top" alt="{{ item.name }}" style="height: 200px; object-fit: cover;">
                {% else %}
                    <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                        <i class="fas fa-pizza-slice fa-3x text-muted"></i>
                    </div>
                {% endif %}
                
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">{{ item.name }}</h5>
                    <p class="card-text flex-grow-1">{{ item.description|truncatewords:20 }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="h5 text-danger mb-0">${{ item.price }}</span>
                        <div>
                            <a href="{% url 'menu:menu_detail' item.pk %}" class="btn btn-outline-danger btn-sm">Details</a>
                            <a href="{% url 'orders:add_to_cart' item.pk %}" class="btn btn-danger btn-sm">
                                <i class="fas fa-cart-plus"></i> Add to Cart
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {% empty %}
        <div class="col-12">
            <div class="alert alert-info text-center">
                <h4>No items found</h4>
                <p>Try adjusting your search or filter criteria.</p>
            </div>
        </div>
    {% endfor %}
</div>
{% endblock %}
"""

# templates/menu/menu_detail.html
"""
{% extends 'base.html' %}

{% block title %}{{ item.name }} - Pizza Palace{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-6">
        {% if item.image %}
            <img src="{{ item.image.url }}" class="img-fluid rounded" alt="{{ item.name }}">
        {% else %}
            <div class="bg-light rounded d-flex align-items-center justify-content-center" style="height: 400px;">
                <i class="fas fa-pizza-slice fa-5x text-muted"></i>
            </div>
        {% endif %}
    </div>
    
    <div class="col-md-6">
        <h2>{{ item.name }}</h2>
        <p class="text-muted">{{ item.get_category_display }}</p>
        <p class="lead">{{ item.description }}</p>
        
        <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="h3 text-danger">${{ item.price }}</span>
        </div>
        
        <div class="d-grid gap-2">
            <a href="{% url 'orders:add_to_cart' item.pk %}" class="btn btn-danger btn-lg">
                <i class="fas fa-cart-plus"></i> Add to Cart
            </a>
            <a href="{% url 'menu:menu_list' %}" class="btn btn-outline-secondary">
                <i class="fas fa-arrow-left"></i> Back to Menu
            </a>
        </div>
    </div>
</div>
{% endblock %}
"""

# templates/orders/cart.html
"""
{% extends 'base.html' %}

{% block title %}Shopping Cart - Pizza Palace{% endblock %}

{% block content %}
<h2>Shopping Cart</h2>

{% if items %}
    <div class="card">
        <div class="card-body">
            {% for item in items %}
                <div class="row align-items-center border-bottom py-3">
                    <div class="col-md-2">
                        {% if item.menu_item.image %}
                            <img src="{{ item.menu_item.image.url }}" class="img-fluid rounded" alt="{{ item.menu_item.name }}">
                        {% else %}
                            <div class="bg-light rounded d-flex align-items-center justify-content-center" style="height: 80px;">
                                <i class="fas fa-pizza-slice text-muted"></i>
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="col-md-4">
                        <h5>{{ item.menu_item.name }}</h5>
                        <p class="text-muted mb-0">${{ item.menu_item.price }} each</p>
                    </div>
                    
                    <div class="col-md-3">
                        <form method="post" action="{% url 'orders:update_cart_quantity' item.menu_item.pk %}" class="d-flex align-items-center">
                            {% csrf_token %}
                            <button type="button" class="btn btn-outline-secondary btn-sm" onclick="decreaseQuantity(this)">-</button>
                            <input type="number" name="quantity" value="{{ item.quantity }}" min="1" class="form-control mx-2 text-center" style="width: 80px;">
                            <button type="button" class="btn btn-outline-secondary btn-sm" onclick="increaseQuantity(this)">+</button>
                            <button type="submit" class="btn btn-sm btn-primary ms-2">Update</button>
                        </form>
                    </div>
                    
                    <div class="col-md-2">
                        <strong>${{ item.total }}</strong>
                    </div>
                    
                    <div class="col-md-1">
                        <a href="{% url 'orders:remove_from_cart' item.menu_item.pk %}" class="btn btn-outline-danger btn-sm">
                            <i class="fas fa-trash"></i>
                        </a>
                    </div>
                </div>
            {% endfor %}
            
            <div class="row mt-3">
                <div class="col-md-8"></div>
                <div class="col-md-4">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h5>Order Summary</h5>
                            <div class="d-flex justify-content-between">
                                <span>Total:</span>
                                <strong class="text-danger">${{ total }}</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="d-flex justify-content-between mt-4">
        <a href="{% url 'menu:menu_list' %}" class="btn btn-outline-secondary">
            <i class="fas fa-arrow-left"></i> Continue Shopping
        </a>
        <a href="{% url 'orders:checkout' %}" class="btn btn-danger btn-lg">
            <i class="fas fa-credit-card"></i> Proceed to Checkout
        </a>
    </div>
{% else %}
    <div class="text-center py-5">
        <i class="fas fa-shopping-cart fa-5x text-muted mb-3"></i>
        <h3>Your cart is empty</h3>
        <p class="text-muted">Add some delicious pizzas to get started!</p>
        <a href="{% url 'menu:menu_list' %}" class="btn btn-danger">Browse Menu</a>
    </div>
{% endif %}

<script>
function increaseQuantity(button) {
    const input = button.previousElementSibling;
    input.value = parseInt(input.value) + 1;
}

function decreaseQuantity(button) {
    const input = button.nextElementSibling;
    if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
    }
}
</script>
{% endblock %}
"""