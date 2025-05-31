from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import MenuItem

# Create your views here.

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