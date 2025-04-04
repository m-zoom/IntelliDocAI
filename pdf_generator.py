# pdf_generator.py - Generate PDF documents
import os
import logging
from typing import List, Dict, Any, Optional
from fpdf import FPDF

from models import DocumentContent, DocumentSection

class PDFGenerator:
    """Generates PDF documents from structured content"""
    
    def __init__(self):
        self.pdf = None
    
    def generate_pdf(self, content: DocumentContent, output_file: str) -> None:
        """Generate a PDF document from structured content"""
        try:
            # Initialize PDF
            self.pdf = FPDF()
            self.pdf.set_auto_page_break(auto=True, margin=15)
            self.pdf.add_page()
            
            # Add document title
            self._add_title(content.title)
            
            # Add introduction
            self._add_section_title("Introduction")
            self._add_text(content.introduction)
            
            # Add main content sections
            for section in content.sections:
                self._add_section_title(section.title)
                self._add_text(section.content)
            
            # Add conclusion
            if content.conclusion:
                self._add_section_title("Conclusion")
                self._add_text(content.conclusion)
            
            # Add references if available
            if content.references:
                self._add_section_title("References")
                for i, reference in enumerate(content.references, 1):
                    self._add_reference(i, reference)
            
            # Save the PDF
            self.pdf.output(output_file)
            logging.info(f"PDF document saved to {output_file}")
            
        except Exception as e:
            logging.error(f"Error generating PDF: {str(e)}")
            raise
    
    def _add_title(self, title: str) -> None:
        """Add the document title to the PDF"""
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(0, 10, title, ln=True, align="C")
        self.pdf.ln(10)
    
    def _add_section_title(self, title: str) -> None:
        """Add a section title to the PDF"""
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 10, title, ln=True)
        self.pdf.ln(2)
    
    def _add_text(self, text: str) -> None:
        """Add text content to the PDF"""
        self.pdf.set_font("Arial", "", 11)
        
        # Ensure text is properly encoded
        cleaned_text = text.encode('latin-1', 'replace').decode('latin-1')
        
        # Add paragraph with line breaks
        for paragraph in cleaned_text.split('\n\n'):
            # Clean up extra whitespace within the paragraph
            paragraph = ' '.join(paragraph.split())
            
            self.pdf.multi_cell(0, 5, paragraph)
            self.pdf.ln(5)
    
    def _add_reference(self, index: int, reference: str) -> None:
        """Add a reference item to the PDF"""
        self.pdf.set_font("Arial", "", 10)
        
        # Ensure text is properly encoded
        cleaned_reference = reference.encode('latin-1', 'replace').decode('latin-1')
        
        self.pdf.multi_cell(0, 5, f"{index}. {cleaned_reference}")
        self.pdf.ln(2)
