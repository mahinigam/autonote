from PIL import Image
import pytesseract
import os

def image_to_text(image_path: str) -> str:
    """Extract text from image using OCR"""
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Open and process image
        image = Image.open(image_path)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Extract text using tesseract
        text = pytesseract.image_to_string(image, lang='eng')
        
        # Close image to free memory
        image.close()
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")
