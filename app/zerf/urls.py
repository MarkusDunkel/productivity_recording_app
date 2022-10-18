from django.urls import path

from . import views

urlpatterns = [
    path('<str:in_date>', views.index, name='index'),
    path('add_entry/<str:in_date>/', views.add_entry, name = 'add_entry')
]