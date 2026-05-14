from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'user_type', 'phone', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Identifiants invalides")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','image','cover_image','email', 'first_name', 'last_name', 'user_type', 'phone', 'date_joined']


# serializers/password_reset_serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import PasswordResetOTP



User = get_user_model()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Aucun utilisateur trouvé avec cet email")
    
    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        
        # Générer un code OTP à 4 chiffres
        otp_code = PasswordResetOTP.generate_otp()
        
        # Supprimer les anciens OTP non utilisés
        PasswordResetOTP.objects.filter(user=user, is_used=False).delete()
        
        # Créer un nouvel OTP
        otp = PasswordResetOTP.objects.create(
            user=user,
            otp_code=otp_code
        )
        
        return {
            'user': user,
            'otp': otp,
            'otp_code': otp_code
        }

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        # Vérifier que les mots de passe correspondent
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas"})
        
        # Vérifier l'existence de l'utilisateur
        try:
            user = User.objects.get(email=data['email'])
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Aucun utilisateur trouvé avec cet email"})
        
        # Vérifier l'OTP
        try:
            otp = PasswordResetOTP.objects.get(
                user=user,
                otp_code=data['otp_code'],
                is_used=False
            )
            if not otp.is_valid():
                raise serializers.ValidationError({"otp_code": "Le code OTP a expiré"})
            data['otp'] = otp
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({"otp_code": "Code OTP invalide"})
        
        return data
    
    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        
        # Mettre à jour le mot de passe
        user.set_password(new_password)
        user.save()
        
        # Marquer l'OTP comme utilisé
        otp = self.validated_data['otp']
        otp.is_used = True
        otp.save()
        
        return user