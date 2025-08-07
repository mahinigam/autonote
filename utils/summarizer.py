import os
import requests
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
    """Generate structured notes from text - now with offline AI"""
    # Try offline AI first (best quality)
    try:
        return generate_notes_ai(text)
    except Exception as ai_error:
        print(f"Offline AI failed: {ai_error}")
    
    # Try OpenAI API if available (fallback)
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            return generate_notes_openai(text, openai_key)
    except Exception as openai_error:
        print(f"OpenAI API failed: {openai_error}")
    
    # Final fallback to simple summarizer
    return simple_text_summarizer(text)

def generate_notes_openai(text: str, api_key: str) -> str:
    """Generate notes using OpenAI API"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {
                'role': 'system',
                'content': 'Convert the following text into structured bullet points. Focus on key information and main ideas. Format as bullet points using •'
            },
            {
                'role': 'user',
                'content': text[:4000]  # Limit text length
            }
        ],
        'max_tokens': 500,
        'temperature': 0.3
    }
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"OpenAI API error: {response.status_code}")
