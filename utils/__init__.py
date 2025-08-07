# Utils package for autonote
# Contains utilities for text extraction and file processing

from .ocr import image_to_text
from .pdf_reader import pdf_to_text
from .docx_reader import docx_to_text
from .summarizer import generate_notes
from .ai_summarizer import generate_notes_ai
from .file_exports import save_as_txt, save_as_md, save_as_pdf, save_as_docx
from .cleanup import cleanup_old_files, start_background_cleanup
from .chatbot import chat_with_document, get_chatbot

__all__ = [
    'image_to_text',
    'pdf_to_text', 
    'docx_to_text',
    'generate_notes',
    'generate_notes_ai',
    'save_as_txt',
    'save_as_md', 
    'save_as_pdf',
    'save_as_docx',
    'cleanup_old_files',
    'start_background_cleanup',
    'chat_with_document',
    'get_chatbot'
]