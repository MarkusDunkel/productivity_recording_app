from django.urls import path

from . import views

urlpatterns = [
    path('<str:in_date>', views.index, name='index'),
    path('', views.redirect_view, name='redirect_view'),
    path('add_entry/<str:in_date>/', views.add_entry, name = 'add_entry')
]