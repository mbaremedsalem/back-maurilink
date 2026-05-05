from django.urls import path
from . import views

urlpatterns = [
    path('create-company/', views.CompanyCreateView.as_view(), name='create-company'),
    path('my-company/', views.CompanyDetailView.as_view(), name='my-company'),
]