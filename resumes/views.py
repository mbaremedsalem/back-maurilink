from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Resume
from .serializers import ResumeSerializer

class ResumeListCreateView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Si c'est le premier CV, le mettre par défaut
        user_resumes = Resume.objects.filter(user=self.request.user)
        is_default = len(user_resumes) == 0
        
        serializer.save(user=self.request.user, is_default=is_default)

class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

class SetDefaultResumeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            # Mettre à jour tous les CVs
            Resume.objects.filter(user=request.user).update(is_default=False)
            # Définir le CV sélectionné comme défaut
            resume = Resume.objects.get(pk=pk, user=request.user)
            resume.is_default = True
            resume.save()
            return Response({"detail": "CV par défaut mis à jour"})
        except Resume.DoesNotExist:
            return Response({"detail": "CV non trouvé"}, status=404)