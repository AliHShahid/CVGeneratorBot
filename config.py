import os

# Model configurations
# NER_MODEL = "dslim/bert-base-NER"
NER_MODEL = "nakamoto-yama/t5-resume-generation"
SUMMARIZATION_MODEL = "sshleifer/distilbart-cnn-12-6"

# German CV Template (matching the provided format)
GERMAN_CV_TEMPLATE = """
+----------------------+-----------------------+----------------------+
| **Titel des Job      |                       |                      |
| Postings**           |                       |                      |
+======================+=======================+======================+
|                      | **angefragt**         | **falls              |
|                      |                       | abweichend**         |
+----------------------+-----------------------+----------------------+
| **Einkaufskurzprofil | {{ einkaufskurzprofil }} | {{ einkaufskurzprofil_alt }} |
| (EKP)**              |                       |                      |
+----------------------+-----------------------+----------------------+
| **Stundenverrechnungs| **{{ stundenverrechnungssatz }}** | **€**     |
| satz (SVS)**         |                       |                      |
+----------------------+-----------------------+----------------------+
| **Möglicher          | {{ starttermin }}     |                      |
| Starttermin**        |                       |                      |
+----------------------+-----------------------+----------------------+

**Berufserfahrung:**

{% for experience in berufserfahrung %}
+------------+---------------------------------------------------------+
| **{{ experience.period }}** | {{ experience.company }}                |
|            |                                                         |
|            | {{ experience.description }}                            |
+============+=========================================================+
{% endfor %}

**Ausbildung:**

{% for education in ausbildung %}
+------------+---------------------------------------------------------+
| **{{ education.period }}** | {{ education.institution }}             |
|            |                                                         |
|            | {{ education.description }}                             |
+============+=========================================================+
{% endfor %}

**Kompetenzen:**

+-------------------------------+--------------------------------------+
| EDV-Kenntnisse:               |                                      |
+===============================+======================================+
{% for skill in edv_kenntnisse %}
| {{ skill }}:                  | Advanced                             |
+-------------------------------+--------------------------------------+
{% endfor %}

Sonstige Techniken:

+--------------------------------+-------------------------------------+
{% for skill in sonstige_techniken %}
| {{ skill }}:                   | Advanced                            |
+================================+=====================================+
{% endfor %}

Sprachkenntnisse:

+--------------------------------+-------------------------------------+
{% for language in sprachkenntnisse %}
| {{ language }}:                | Advanced                            |
+================================+=====================================+
{% endfor %}

**Zusätzliche Bemerkungen**

+-----------------------------------------------------------------------+
| {{ zusaetzliche_bemerkungen }}                                        |
+=======================================================================+
"""

# Default template for backward compatibility
# DEFAULT_TEMPLATE = """
# Kandidatenprofil:

# Name: {{ name }}
# E-Mail: {{ email }}
# Telefon: {{ phone }}
# Fähigkeiten: {{ skills }}
# Zusammenfassung der Berufserfahrung: {{ summary }}
# """

# Output configurations
OUTPUT_DIR = "output"
# DEFAULT_DOCX_FILENAME = "Bewerberprofil_SAP_Meister_Techniker.docx"
from datetime import datetime

DEFAULT_DOCX_FILENAME = "Bewerberprofil.docx"

# Add current date
# date_str = datetime.now().strftime("%Y%m%d")
# filename_with_date = f"Bewerberprofil_{date_str}.docx"

# Add date and time
datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
filename_with_datetime = f"Bewerberprofil_{datetime_str}.docx"

# Processing configurations
SUMMARY_MAX_LENGTH = 150
SUMMARY_MIN_LENGTH = 40

# File type configurations
ALLOWED_PDF_EXTENSIONS = [".pdf"]
ALLOWED_DOCX_EXTENSIONS = [".docx"]

# Gradio configurations
GRADIO_SHARE = True
GRADIO_DEBUG = False

# German CV specific configurations
DEFAULT_JOB_TITLE = "SAP Meister/Techniker"
DEFAULT_EKP = "X|YYY|XXX|Z"
DEFAULT_SVS = "€"
DEFAULT_START_DATE = "01.04.2025"

# Skills categories for German format
EDV_SKILLS = [
    "MS-Word", "MS-Excel", "MS-Outlook", "SAP", "Python", "Java", 
    "JavaScript", "SQL", "HTML", "CSS", "PowerPoint", "Access"
]

TECHNICAL_SKILLS = [
    "Schienenfahrzeugbau", "Dokumentation", "Koordination", 
    "Projektmanagement", "Qualitätssicherung", "Mechanik", 
    "Hydraulik", "Pneumatik", "Elektrik"
]

LANGUAGES = [
    "Deutsch", "Englisch", "Französisch", "Spanisch", "Italienisch"
]

# Template styling
CSS_STYLES = """
.cv-container {
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.cv-header {
    border: 1px solid #000;
    margin-bottom: 20px;
}

.cv-section {
    margin-bottom: 20px;
}

.cv-table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #000;
}

.cv-table th, .cv-table td {
    border: 1px solid #000;
    padding: 8px;
    text-align: left;
}

.cv-table th {
    background-color: #f2f2f2;
    font-weight: bold;
}
"""