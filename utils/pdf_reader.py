import fitz  # PyMuPDF
import os
import tempfile
from typing import Union
from .ocr import image_to_text

def extract_images_from_pdf_page(page, page_num: int):
    """Extract images from a PDF page and perform OCR on them"""
    extracted_text = ""
    
    try:
        # Get list of images on the page
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            # Get image object
            xref = img[0]
            pix = fitz.Pixmap(page.parent, xref)
            
            # Convert to PNG bytes if needed
            if pix.n - pix.alpha < 4:  # GRAY or RGB
                # Save image temporarily
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    if pix.n - pix.alpha == 1:  # GRAY
                        pix.pil_save(temp_file.name, format="PNG")
                    else:  # RGB
                        pix.pil_save(temp_file.name, format="PNG")
                    
                    temp_path = temp_file.name
                
                try:
                    # Perform OCR on the extracted image
                    image_text = image_to_text(temp_path)
                    if image_text and image_text.strip():
                        extracted_text += f"\n[Image {page_num}-{img_index}]: {image_text.strip()}\n"
                except Exception as ocr_error:
                    print(f"OCR failed for image {page_num}-{img_index}: {ocr_error}")
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            pix = None  # Free memory
            
    except Exception as e:
        print(f"Error extracting images from page {page_num}: {e}")
    
    return extracted_text

def pdf_to_text(pdf_path: str) -> str:
    """Extract text and images from PDF file using PyMuPDF"""
    text = ""
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract text from the page
            page_text = page.get_text()
            if page_text and page_text.strip():
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text + "\n"
            
            # Extract and OCR images from the page
            image_text = extract_images_from_pdf_page(page, page_num + 1)
            if image_text:
                text += image_text
        
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
