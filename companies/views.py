from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer

class CompanyCreateView(generics.CreateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Vérifier si l'utilisateur est bien une entreprise
        if self.request.user.user_type != 'company':
            return Response(
                {"detail": "Seuls les comptes entreprise peuvent créer un profil d'entreprise"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(user=self.request.user)

class CompanyDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)
    
    def get_object(self):
        return self.get_queryset().first()