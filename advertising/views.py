from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Advertisement
from .serializers import AdvertisementSerializer

class AdvertisementListCreateView(generics.ListCreateAPIView):
    serializer_class = AdvertisementSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        # Les publicités actives dans la période
        from django.utils import timezone
        queryset = Advertisement.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        return queryset
    
    def perform_create(self, serializer):
        if hasattr(self.request.user, 'company_profile'):
            serializer.save(company=self.request.user.company_profile)

class TrackAdView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, pk, action):
        try:
            ad = Advertisement.objects.get(pk=pk)
            if action == 'view':
                ad.views_count += 1
            elif action == 'click':
                ad.clicks_count += 1
            ad.save()
            return Response({"detail": "Tracked"})
        except Advertisement.DoesNotExist:
            return Response({"detail": "Publicité non trouvée"}, status=404)