import fitz  # PyMuPDF

def pdf_to_text(pdf_path: str) -> str:
    """Extract text from PDF file using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        # Fallback to pdfminer if PyMuPDF fails
        try:
            from pdfminer.high_level import extract_text
            return extract_text(pdf_path)
        except Exception as fallback_error:
            raise Exception(f"Error reading PDF with both PyMuPDF and pdfminer: {str(e)}, {str(fallback_error)}")
