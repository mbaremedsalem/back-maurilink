from rest_framework import serializers
from .models import Advertisement

class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'
        read_only_fields = ['company', 'views_count', 'clicks_count', 'created_at']