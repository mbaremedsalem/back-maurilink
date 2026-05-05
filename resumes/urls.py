from django.urls import path
from . import views

urlpatterns = [
    path('resumes/', views.ResumeListCreateView.as_view(), name='resumes-list'),
    path('resumes/<int:pk>/', views.ResumeDetailView.as_view(), name='resume-detail'),
    path('resumes/<int:pk>/set-default/', views.SetDefaultResumeView.as_view(), name='set-default-resume'),
]