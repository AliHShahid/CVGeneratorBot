import gradio as gr
import torch
import fitz
from docx import Document
import os
from datetime import datetime

from models import get_cv_processor, extract_candidate_data
from utils import (
    create_output_directory,
    read_pdf_content,
    create_german_cv_docx,
    format_profile_text
)
from config import (
    DEFAULT_JOB_TITLE,
    DEFAULT_EKP,
    DEFAULT_SVS,
    DEFAULT_START_DATE,
    DEFAULT_DOCX_FILENAME
)

# Configure transformers logging
import transformers
transformers.logging.set_verbosity_error()

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from an uploaded PDF file.
    """
    return read_pdf_content(pdf_file.name)

def generate_profile_from_text(cv_text: str, references: str = "", certificates: str = "") -> dict:
    """
    Generate a comprehensive profile from CV text, references, and certificates.
    """
    # Extract structured data from CV text using the processor
    extracted_data = extract_candidate_data(cv_text)
    
    # Add default values if not found
    if not extracted_data.get('job_title'):
        extracted_data['job_title'] = DEFAULT_JOB_TITLE
    if not extracted_data.get('einkaufskurzprofil'):
        extracted_data['einkaufskurzprofil'] = DEFAULT_EKP
    if not extracted_data.get('stundenverrechnungssatz'):
        extracted_data['stundenverrechnungssatz'] = DEFAULT_SVS
    if not extracted_data.get('starttermin'):
        extracted_data['starttermin'] = DEFAULT_START_DATE
    
    # Add references and certificates if provided
    if references:
        extracted_data['referenzen'] = references
    if certificates:
        extracted_data['zertifikate'] = certificates
    
    # Format the additional remarks
    remarks = extracted_data.get('zusaetzliche_bemerkungen', '')
    if references or certificates:
        remarks += "\n\nZusätzliche Informationen:\n"
        if references:
            remarks += f"- Referenzen: {references}\n"
        if certificates:
            remarks += f"- Zertifikate: {certificates}\n"
    
    extracted_data['zusaetzliche_bemerkungen'] = remarks
    
    return extracted_data

def create_docx_profile(profile_data: dict) -> str:
    """
    Create a DOCX file from the profile data.
    """
    return create_german_cv_docx(profile_data, DEFAULT_DOCX_FILENAME)

def handle_inputs(text_input: str, pdf_file, references: str, certificates: str):
    """
    Handle both text and PDF inputs and generate profile.
    """
    # Extract text from PDF if provided
    if pdf_file:
        text_input = extract_text_from_pdf(pdf_file)
    
    if not text_input or not text_input.strip():
        return "⚠️ Kein Text gefunden im Lebenslauf.", None
    
    # Generate profile
    profile_data = generate_profile_from_text(text_input, references, certificates)
    
    # Format text output
    formatted_text = format_profile_text(profile_data)
    
    # Create DOCX file
    docx_path = create_docx_profile(profile_data)
    
    return formatted_text, docx_path

# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Kandidatenprofil Generator", css="""
        .logo-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo-container img {
            max-width: 300px;
            height: auto;
        }
        #title {
            text-align: center;
            margin-top: 10px;
        }
    """) as demo:
        # with gr.Row():
            # gr.HTML("""
            #     <div class="logo-container">
            #         <img src="logo.jpg" alt="iSK Personaldienstleistungen" />
            #     </div>
            # """)
        gr.Image(value="static/logo1.jpg", type="filepath", label=None, show_label=False, height=100, width=100)
        gr.Markdown("## 👥 **Automatisches Kandidatenprofil**<br>powered by KI — Für Personalberater", elem_id="title")

        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(
                    label="Part 1 📄 Lebenslauftext (oder leer lassen und PDF hochladen)", 
                    lines=10, 
                    placeholder="Optional"
                )
                pdf_input = gr.File(
                    label="Part 2 📎 Lebenslauf als PDF hochladen", 
                    file_types=[".pdf"]
                )
                references_input = gr.Textbox(
                    label="Part 3 🗣️ Referenzen / Aussagen", 
                    lines=5, 
                    placeholder="Optional"
                )
                certificates_input = gr.Textbox(
                    label="Part 4 🎓 Zertifikate & Schulungen", 
                    lines=5, 
                    placeholder="Optional"
                )
                generate_btn = gr.Button("🔍 Profil generieren")

            with gr.Column():
                output_text = gr.Textbox(
                    label="Part 5 📌 Generiertes Profil", 
                    lines=20
                )
                file_output = gr.File(
                    label="Part 6 ⬇️ Herunterladen: Word-Datei", 
                    file_types=[".docx"]
                )

        generate_btn.click(
            fn=handle_inputs,
            inputs=[input_text, pdf_input, references_input, certificates_input],
            outputs=[output_text, file_output]
        )

    return demo

if __name__ == "__main__":
    # Initialize the CV processor
    cv_processor = get_cv_processor()
    
    demo = create_interface()
    demo.launch(share=True)