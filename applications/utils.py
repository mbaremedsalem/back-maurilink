# applications/utils.py
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.conf import settings
from django.core.files.base import ContentFile
import os

def generate_resume_pdf(resume_data, user_data):
    """
    Génère un PDF à partir des données du CV
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Style pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E4053'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    # Style pour les sous-titres
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2874A6'),
        spaceAfter=12
    )
    
    # En-tête avec le nom
    name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
    if not name:
        name = user_data.get('username', 'Candidat')
    
    story.append(Paragraph(name, title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Informations de contact
    contact_info = f"""
    <b>Email:</b> {user_data.get('email', 'Non fourni')}<br/>
    <b>Téléphone:</b> {user_data.get('phone', 'Non fourni')}
    """
    story.append(Paragraph(contact_info, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Titre du CV
    if resume_data.get('title'):
        story.append(Paragraph(resume_data['title'], subtitle_style))
        story.append(Spacer(1, 0.1 * inch))
    
    # Compétences
    if resume_data.get('skills'):
        story.append(Paragraph("<b>Compétences:</b>", subtitle_style))
        skills_text = ", ".join(resume_data['skills']) if isinstance(resume_data['skills'], list) else resume_data['skills']
        story.append(Paragraph(skills_text, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
    
    # Expériences
    if resume_data.get('experience'):
        story.append(Paragraph("<b>Expériences professionnelles:</b>", subtitle_style))
        experiences = resume_data['experience'] if isinstance(resume_data['experience'], list) else [resume_data['experience']]
        for exp in experiences:
            if isinstance(exp, dict):
                exp_text = f"<b>{exp.get('title', '')}</b> - {exp.get('company', '')}<br/>{exp.get('description', '')}"
            else:
                exp_text = str(exp)
            story.append(Paragraph(exp_text, styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
    
    # Éducation
    if resume_data.get('education'):
        story.append(Paragraph("<b>Formation:</b>", subtitle_style))
        educations = resume_data['education'] if isinstance(resume_data['education'], list) else [resume_data['education']]
        for edu in educations:
            if isinstance(edu, dict):
                edu_text = f"<b>{edu.get('degree', '')}</b> - {edu.get('institution', '')}<br/>{edu.get('year', '')}"
            else:
                edu_text = str(edu)
            story.append(Paragraph(edu_text, styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
    
    # Langues
    if resume_data.get('languages'):
        story.append(Paragraph("<b>Langues:</b>", subtitle_style))
        languages_text = ", ".join(resume_data['languages']) if isinstance(resume_data['languages'], list) else resume_data['languages']
        story.append(Paragraph(languages_text, styles['Normal']))
    
    # Construction du PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer