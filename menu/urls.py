from django.urls import path
from .views import menu_list, menu_detail

app_name = 'menu'

urlpatterns = [
    path('', menu_list, name='menu_list'),
    path('item/<int:pk>/', menu_detail, name='menu_detail'),
]