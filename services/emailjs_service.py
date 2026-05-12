# services/emailjs_service.py
import requests
import json
from django.conf import settings
from datetime import datetime

class EmailJSService:
    def __init__(self):
        self.public_key = settings.EMAILJS_PUBLIC_KEY
        self.private_key = settings.EMAILJS_PRIVATE_KEY  # Ajouter private key
        self.service_id = settings.EMAILJS_SERVICE_ID
        self.api_url = "https://api.emailjs.com/api/v1.0/email/send"
    
    def send_applications_batch(self, to_email, job_offer, applications):
        # Construire la liste HTML des candidatures
        applications_html = ""
        
        status_mapping = {
            'pending': 'En attente',
            'reviewed': 'Examinée',
            'accepted': 'Acceptée',
            'rejected': 'Refusée',
        }
        
        for app in applications:
            if app.candidate:
                name = f"{app.candidate.first_name} {app.candidate.last_name}".strip() or app.candidate.username
                email = app.candidate.email
            else:
                name = app.candidate_name or "Candidat anonyme"
                email = app.candidate_email or "Non renseigné"
            
            status_display = status_mapping.get(app.status, app.status)
            
            applications_html += f"""
            <div class="application-card">
                <div class="candidate-name">👤 {name}</div>
                <div class="candidate-info">📧 {email}</div>
                <div class="candidate-info">📅 {app.applied_date.strftime('%d/%m/%Y à %H:%M')}</div>
                <span class="status-badge status-{app.status}">{status_display}</span>
            """
            
            if app.cover_letter:
                applications_html += f"""
                <div class="cover-letter">
                    <strong>📝 Lettre de motivation:</strong><br/>
                    {app.cover_letter[:300]}{'...' if len(app.cover_letter) > 300 else ''}
                </div>
                """
            
            applications_html += "</div>"
        
        # Paramètres du template
        template_params = {
            'job_title': job_offer.title,
            'job_location': job_offer.location,
            'total_applications': len(applications),
            'applications_list': applications_html,
            'company_name': job_offer.company.company_name,
            'current_date': datetime.now().strftime('%d/%m/%Y à %H:%M'),
            'to_email': to_email,
        }
        
        # Pour Private Key, utiliser accessToken au lieu de user_id
        # ET ajouter le paramètre 'accessToken'
        payload = {
            'service_id': self.service_id,
            'template_id': settings.EMAILJS_TEMPLATE_BATCH,
            'accessToken': self.private_key,  # Note: 'accessToken' pour private key
            'template_params': template_params
        }
        
        try:
            response = requests.post(
                self.api_url, 
                data=json.dumps(payload), 
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"EmailJS Response Status: {response.status_code}")
            print(f"EmailJS Response Body: {response.text}")
            
            if response.status_code == 200:
                print(f"Email sent successfully to {to_email}")
                return True
            else:
                print(f"EmailJS error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"EmailJS request error: {str(e)}")
            return False
        except Exception as e:
            print(f"EmailJS unexpected error: {str(e)}")
            return False