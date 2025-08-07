import os
from .ai_summarizer import generate_notes_ai

def simple_text_summarizer(text: str) -> str:
    """Simple fallback summarizer without AI dependencies"""
    if not text or not text.strip():
        return "• No content provided"
    
    sentences = text.strip().split('.')
    if len(sentences) <= 3:
        return f"• {text.strip()}"
    
    # Take first and last few sentences as summary
    summary_sentences = sentences[:2] + sentences[-1:]
    bullet_points = []
    
    for sentence in summary_sentences:
        cleaned = sentence.strip()
        if cleaned and len(cleaned) > 10:
            bullet_points.append(f"• {cleaned}")

    return "\n".join(bullet_points) if bullet_points else f"• {text[:200]}..."

def generate_notes(text: str) -> str:
    """Generate structured notes from text using offline AI"""
    # Try offline AI first (primary method)
    try:
        return generate_notes_ai(text)
    except Exception as ai_error:
        print(f"Offline AI failed: {ai_error}")
    
    # Fallback to simple summarizer
    return simple_text_summarizer(text)
