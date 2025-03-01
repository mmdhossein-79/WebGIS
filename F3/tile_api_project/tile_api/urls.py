from django.urls import path
from . import views

urlpatterns = [
    path('tile/', views.get_tile, name='get_tile'),
]