from django.urls import path
from . import views

urlpatterns = [
    path('ads/', views.AdvertisementListCreateView.as_view(), name='ads-list'),
    path('ads/<int:pk>/track/<str:action>/', views.TrackAdView.as_view(), name='track-ad'),
]