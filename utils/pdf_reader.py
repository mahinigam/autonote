import fitz  # PyMuPDF
import os
from typing import Union

def pdf_to_text(pdf_path: str) -> str:
    """Extract text from PDF file using PyMuPDF"""
    text = ""
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract text from the page
            page_text = page.get_text() # type: ignore
            if page_text and page_text.strip():
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text + "\n"
        
        doc.close()
        
        if text.strip():
            return text.strip()
        else:
            # If no text found with PyMuPDF, try pdfminer as fallback
            raise Exception("No text extracted with PyMuPDF")
            
    except Exception as pymupdf_error:
        # Fallback to pdfminer if PyMuPDF fails
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(pdf_path)
            if text and text.strip():
                return text.strip()
            else:
                raise Exception("No text found in PDF")
        except Exception as pdfminer_error:
            raise Exception(f"Error reading PDF with both libraries. PyMuPDF: {str(pymupdf_error)}, pdfminer: {str(pdfminer_error)}")
