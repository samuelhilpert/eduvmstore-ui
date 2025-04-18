from http.client import responses

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.utils.translation import gettext_lazy as _

import requests
from django.views.decorators.csrf import csrf_exempt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from io import BytesIO
from django.http import HttpResponse



class IndexView(generic.TemplateView):
    """
        View for displaying the tutorial index page and handling data retrieval from a backend API.
    """
    template_name = 'eduvmstore_dashboard/tutorial/index.html'
    page_title = _("About EduVMStore")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context

    def post(self, request, *args, **kwargs):
        pdf_bytes = generate_eduvmstore_pdf()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="EduVMStore.pdf"'
        return response

def generate_eduvmstore_pdf():
    """
    Erstellt ein PDF mit Text- und Code-Inhalten und gibt es als Bytes zurück.
    Ideal für Webanwendungen (z. B. Flask/FastAPI).
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterHeading', parent=styles['Heading1'], alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='CodeBlock', fontName='Courier', fontSize=9, leading=12, spaceBefore=6, spaceAfter=6))

    elements = []

    # Beispielinhalte – hier kannst du deinen echten Text einsetzen
    sections = [
        {
            "title": "Einführung",
            "text": """EduVMStore ist eine Plattform zur Verwaltung virtueller Maschinen für Bildungszwecke.
Sie basiert auf OpenStack und ermöglicht Dozierenden und Studierenden eine einfache Handhabung von VMs.
Dieses Dokument fasst alle Anleitungen, Tutorials und Beispiele zusammen."""
        },
        {
            "title": "Kurzanleitung: AppTemplate erstellen",
            "text": """1. Dashboard öffnen
2. 'Create AppTemplate' klicken
3. Image auswählen
4. Name und Beschreibung eintragen
5. Cloud-Init-Skript schreiben oder hochladen
6. Speichern und fertigstellen"""
        },
        {
            "title": "Beispiel: Cloud-Init-Skript (SSH für Nutzer)",
            "code": """
runcmd:
  - |
    while IFS=':' read -r username password; do
      useradd -m -s /bin/bash "$username"
      echo "$username:$password" | chpasswd
    done < /etc/users.txt
"""
        }
    ]

    for section in sections:
        elements.append(Paragraph(section['title'], styles['CenterHeading']))
        elements.append(Spacer(1, 12))

        if "text" in section:
            for line in section["text"].split('\n'):
                elements.append(Paragraph(line.strip(), styles['Normal']))
                elements.append(Spacer(1, 6))

        if "code" in section:
            elements.append(Preformatted(section["code"].strip(), styles['CodeBlock']))
            elements.append(Spacer(1, 12))

        elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()