#!/usr/bin/env python3
"""
Simple test script for autonote functionality
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from config import Config
        print("✓ Config imported successfully")
        
        from utils.summarizer import generate_notes
        print("✓ Summarizer imported successfully")
        
        from utils.ocr import image_to_text
        print("✓ OCR module imported successfully")
        
        from utils.pdf_reader import pdf_to_text
        print("✓ PDF reader imported successfully")
        
        from utils.docx_reader import docx_to_text
        print("✓ DOCX reader imported successfully")
        
        from utils.file_exports import save_as_txt, save_as_md, save_as_pdf, save_as_docx
        print("✓ File exports imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_summarizer():
    """Test the summarizer with sample text"""
    try:
        from utils.summarizer import generate_notes
        
        sample_text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans. 
        Leading AI textbooks define the field as the study of "intelligent agents": 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals. The term "artificial intelligence" 
        is often used to describe machines that mimic cognitive functions that humans 
        associate with the human mind, such as learning and problem solving.
        """
        
        notes = generate_notes(sample_text)
        print("✓ Summarizer test successful")
        print(f"Generated notes:\n{notes}")
        return True
    except Exception as e:
        print(f"✗ Summarizer test failed: {e}")
        return False

def test_flask_app():
    """Test that Flask app can be created"""
    try:
        from app import app
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running autonote tests...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Summarizer Test", test_summarizer),
        ("Flask App Test", test_flask_app),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        
    print(f"\n--- Test Results ---")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
