import torch
from transformers import pipeline
import transformers
from typing import Dict, List
import re
from datetime import datetime
from config import NER_MODEL, SUMMARIZATION_MODEL, SUMMARY_MAX_LENGTH, SUMMARY_MIN_LENGTH

# Configure transformers logging
transformers.logging.set_verbosity_error()

class CVProcessor:
    """Main class for processing CV data using transformer models."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.ner_pipeline = None
        self.summarizer = None
        self._load_models()
    
    # In models.py, update the _load_models method:

    def _load_models(self):
        """Load the required transformer models."""
        print("Loading models...")
        try:
        # Load NER pipeline with updated parameters
            self.ner_pipeline = pipeline(
                "ner", 
                model=NER_MODEL, 
                aggregation_strategy="simple",  # Use this instead of grouped_entities
                device=0 if self.device == "cuda" else -1
                )
        
        # Load summarization pipeline
            self.summarizer = pipeline(
                "summarization", 
                model=SUMMARIZATION_MODEL,
                device=0 if self.device == "cuda" else -1
            )
        
            print(f"Models loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading models: {e}")
            raise
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text."""
        if not self.ner_pipeline:
            raise ValueError("NER pipeline not loaded")
        
        try:
            return self.ner_pipeline(text)
        except Exception as e:
            print(f"Error in entity extraction: {e}")
            return []
    
    def summarize_text(self, text: str) -> str:
        """Summarize the input text."""
        if not self.summarizer:
            raise ValueError("Summarizer pipeline not loaded")
        
        try:
            # Limit input text length to avoid memory issues
            max_input_length = 1024
            if len(text) > max_input_length:
                text = text[:max_input_length]
            
            summary = self.summarizer(
                text, 
                max_length=SUMMARY_MAX_LENGTH, 
                min_length=SUMMARY_MIN_LENGTH, 
                do_sample=False
            )
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Error in text summarization: {e}")
            return "Zusammenfassung konnte nicht erstellt werden."
    
    def extract_work_experience(self, text: str) -> List[Dict]:
        """Extract work experience entries from text."""
        experiences = []
        
        # Look for date patterns and company names
        date_pattern = r'(\d{1,2}\/\d{4}|\d{4})\s*[-–]\s*(\d{1,2}\/\d{4}|\d{4}|dato|heute)'
        company_pattern = r'([A-ZÄÖÜÄ][a-zäöüß\s&,.-]+(?:AG|GmbH|KG|e\.V\.|Inc\.|Ltd\.|Co\.))'
        
        # Split text into sections
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            if any(keyword in section.lower() for keyword in ['erfahrung', 'tätigkeit', 'position', 'stelle']):
                # Extract dates
                dates = re.findall(date_pattern, section)
                # Extract companies
                companies = re.findall(company_pattern, section)
                
                if dates and companies:
                    experience = {
                        'period': f"{dates[0][0]} - {dates[0][1]}",
                        'company': companies[0],
                        'description': section.strip()
                    }
                    experiences.append(experience)
        
        return experiences
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education entries from text."""
        education = []
        
        # Look for education keywords and patterns
        education_keywords = ['ausbildung', 'studium', 'weiterbildung', 'abschluss', 'universität', 'hochschule', 'schule']
        date_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|dato|heute)'
        
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            if any(keyword in section.lower() for keyword in education_keywords):
                dates = re.findall(date_pattern, section)
                
                education_entry = {
                    'period': f"{dates[0][0]} - {dates[0][1]}" if dates else "",
                    'institution': "",
                    'degree': "",
                    'description': section.strip()
                }
                education.append(education_entry)
        
        return education
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills categorized by type."""
        skills = {
            'edv_kenntnisse': [],
            'sonstige_techniken': [],
            'sprachkenntnisse': []
        }
        
        # IT/Software skills
        it_skills = ['SAP', 'MS-Word', 'MS-Excel', 'MS-Outlook', 'Python', 'Java', 'SQL', 'HTML', 'CSS']
        
        # Technical skills
        technical_skills = ['Schienenfahrzeugbau', 'Dokumentation', 'Koordination', 'Projektmanagement']
        
        # Languages
        languages = ['Deutsch', 'Englisch', 'Französisch', 'Spanisch', 'Italienisch']
        
        text_lower = text.lower()
        
        for skill in it_skills:
            if skill.lower() in text_lower:
                skills['edv_kenntnisse'].append(skill)
        
        for skill in technical_skills:
            if skill.lower() in text_lower:
                skills['sonstige_techniken'].append(skill)
        
        for lang in languages:
            if lang.lower() in text_lower:
                skills['sprachkenntnisse'].append(lang)
        
        return skills
    
    def extract_candidate_data(self, raw_text: str) -> Dict:
        """Extract structured data from raw input text according to German template."""
        if not raw_text or not raw_text.strip():
            return self._get_empty_template()
        
        # Named Entity Recognition
        ner_results = self.extract_entities(raw_text)
        
        # Basic information extraction
        name = ""
        email = ""
        phone = ""
        
        for entity in ner_results:
            entity_text = entity.get('word', '')
            entity_group = entity.get('entity_group', '')
            
            if entity_group == 'PER' and not name:
                name = entity_text
            elif entity_group == 'MISC' and '@' in entity_text and not email:
                email = entity_text
            elif entity_group == 'MISC' and self._is_phone_number(entity_text) and not phone:
                phone = entity_text
        
        # Extract structured sections
        work_experience = self.extract_work_experience(raw_text)
        education = self.extract_education(raw_text)
        skills = self.extract_skills(raw_text)
        
        # Generate summary
        summary = self.summarize_text(raw_text)
        
        return {
            # Header information
            "job_title": "SAP Meister/Techniker",  # Default from template
            "einkaufskurzprofil": "X|YYY|XXX|Z",  # Default from template
            "stundenverrechnungssatz": "€",
            "starttermin": "01.04.2025",  # Default from template
            
            # Personal information
            "name": name,
            "email": email,
            "phone": phone,
            
            # Professional experience
            "berufserfahrung": work_experience,
            
            # Education
            "ausbildung": education,
            
            # Skills
            "edv_kenntnisse": skills['edv_kenntnisse'],
            "sonstige_techniken": skills['sonstige_techniken'],
            "sprachkenntnisse": skills['sprachkenntnisse'],
            
            # Summary
            "summary": summary,
            "zusaetzliche_bemerkungen": f"Profil automatisch generiert am {datetime.now().strftime('%d.%m.%Y')}"
        }
    
    def _get_empty_template(self) -> Dict:
        """Return empty template structure."""
        return {
            "job_title": "",
            "einkaufskurzprofil": "",
            "stundenverrechnungssatz": "€",
            "starttermin": "",
            "name": "",
            "email": "",
            "phone": "",
            "berufserfahrung": [],
            "ausbildung": [],
            "edv_kenntnisse": [],
            "sonstige_techniken": [],
            "sprachkenntnisse": [],
            "summary": "",
            "zusaetzliche_bemerkungen": ""
        }
    
    def _is_phone_number(self, text: str) -> bool:
        """Check if text looks like a phone number."""
        import re
        # Remove common separators
        clean_text = re.sub(r'[-\s()]', '', text)
        # Check if it's mostly digits and has reasonable length
        return (len(clean_text) >= 7 and 
                len(clean_text) <= 15 and 
                sum(c.isdigit() for c in clean_text) >= len(clean_text) * 0.7)


# Global instance
cv_processor = None

def get_cv_processor() -> CVProcessor:
    """Get or create the global CV processor instance."""
    global cv_processor
    if cv_processor is None:
        cv_processor = CVProcessor()
    return cv_processor

def extract_candidate_data(raw_text: str) -> Dict:
    """Convenience function to extract candidate data."""
    processor = get_cv_processor()
    return processor.extract_candidate_data(raw_text)