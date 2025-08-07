from PIL import Image
import pytesseract
import cv2
import numpy as np
import os

def preprocess_image_for_ocr(image_array):
    """Preprocess image using OpenCV for better OCR results"""
    # Convert to grayscale
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_array
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Apply threshold to get better contrast
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Morphological operations to clean up the image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def image_to_text(image_path: str) -> str:
    """Extract text from image using OCR with enhanced preprocessing"""
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load image with OpenCV for preprocessing
        image_cv = cv2.imread(image_path)
        if image_cv is None:
            # Fallback to PIL if OpenCV can't read the image
            image_pil = Image.open(image_path)
            if image_pil.mode in ("RGBA", "P"):
                image_pil = image_pil.convert("RGB")
            image_array = np.array(image_pil)
        else:
            # Convert BGR to RGB for consistency
            image_array = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        
        # Preprocess image for better OCR
        processed_image = preprocess_image_for_ocr(image_array)
        
        # Convert back to PIL Image for tesseract
        processed_pil = Image.fromarray(processed_image)
        
        # Extract text using tesseract with optimized config
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}"\'-_ '
        text = pytesseract.image_to_string(processed_pil, lang='eng', config=custom_config)
        
        # Clean up extracted text
        cleaned_text = text.strip()
        
        # If no text found with preprocessing, try original image
        if not cleaned_text:
            original_pil = Image.open(image_path)
            if original_pil.mode in ("RGBA", "P"):
                original_pil = original_pil.convert("RGB")
            text = pytesseract.image_to_string(original_pil, lang='eng')
            cleaned_text = text.strip()
        
        return cleaned_text
        
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")
