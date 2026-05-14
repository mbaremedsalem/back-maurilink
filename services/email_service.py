# services/email_service.py
import requests
import json

class EmailJSService:
    def __init__(self):
        self.public_key = 'v1eEa1DGx7pm0Xwwo'
        self.private_key = 'Tkr1bUtnhsb-4_Sirqkmn'
        self.service_id = 'service_j6rlly8'
        self.template_otp_id = 'template_94b5cxc'  # Utilisez votre template ID
        self.api_url = 'https://api.emailjs.com/api/v1.0/email/send'
    
    def send_reset_password_otp(self, user_email, username, otp_code):
        """
        Envoyer le code OTP à l'email spécifié dans le body
        """
        try:
            # Préparer les paramètres pour EmailJS
            template_params = {
                'to_email': user_email,      # ⚠️ CRITIQUE: C'est l'email qui reçoit le code
                'username': username,        # Nom affiché dans l'email
                'otp_code': otp_code,       # Code OTP
                'reply_to': user_email      # Pour pouvoir répondre
            }
            
            # La requête pour EmailJS
            data = {
                'service_id': self.service_id,
                'template_id': self.template_otp_id,
                'user_id': self.public_key,
                'accessToken': self.private_key,
                'template_params': template_params
            }
            
            print(f"📧 Envoi à: {user_email}")
            print(f"📝 Paramètres: {template_params}")
            
            # Envoyer la requête
            response = requests.post(
                self.api_url,
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"📬 Réponse status: {response.status_code}")
            print(f"📄 Réponse texte: {response.text}")
            
            if response.status_code == 200:
                return {
                    'success': True, 
                    'message': f'Code OTP envoyé à {user_email}',
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False, 
                    'message': f"Erreur EmailJS: {response.text}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False, 
                'message': f"Erreur: {str(e)}"
            }

