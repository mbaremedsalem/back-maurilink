from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.ApplicationCreateView.as_view(), name='apply'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='my-applications'),
    path('company-applications/', views.CompanyApplicationsView.as_view(), name='company-applications'),
    path('applications/<int:pk>/update-status/', views.UpdateApplicationStatusView.as_view(), name='update-status'),
]