from transformers import pipeline
import os
import re

MODEL = os.getenv("MODEL_NAME", "sshleifer/distilbart-cnn-12-6")

# Initialize the summarizer pipeline once
summarizer = None
use_fallback = False

try:
    summarizer = pipeline("summarization", model=MODEL)
except Exception as e:
    print(f"Error loading model {MODEL}: {e}")
    try:
        # Try a smaller, more reliable model
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
    except Exception as e2:
        print(f"Error loading fallback model: {e2}")
        # Set flag to use simple text processing fallback
        use_fallback = True

def simple_text_summarizer(text: str) -> str:
    """Simple fallback summarizer using basic text processing"""
    sentences = re.split(r'[.!?]+', text)
    # Filter out very short sentences
    meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Take first few sentences and key sentences
    summary_sentences = []
    
    # Add first sentence
    if meaningful_sentences:
        summary_sentences.append(meaningful_sentences[0])
    
    # Add sentences with important keywords
    keywords = ['important', 'key', 'main', 'significant', 'crucial', 'essential', 'primary']
    for sentence in meaningful_sentences[1:]:
        if any(keyword in sentence.lower() for keyword in keywords):
            summary_sentences.append(sentence)
        if len(summary_sentences) >= 5:
            break
    
    # If still short, add more sentences
    if len(summary_sentences) < 3 and len(meaningful_sentences) > len(summary_sentences):
        remaining_sentences = meaningful_sentences[len(summary_sentences):len(summary_sentences)+3]
        summary_sentences.extend(remaining_sentences)
    
    # Format as bullet points
    bullet_notes = "\n".join([f"• {sentence.strip()}." for sentence in summary_sentences])
    return bullet_notes

def chunk_text(text: str, max_chunk_size: int = 1000) -> list:
    """Split text into smaller chunks for processing"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1  # +1 for space
        
        if current_size >= max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def generate_notes(text: str, max_length: int = 200, min_length: int = 50) -> str:
    """Generate structured bullet-point notes from text"""
    if not text.strip():
        return "No content provided for summarization."
    
    # Use fallback if AI models aren't available
    if use_fallback or summarizer is None:
        return simple_text_summarizer(text)
    
    try:
        # Handle long texts by chunking
        if len(text) > 1000:
            chunks = chunk_text(text, 900)
            summaries = []
            
            for chunk in chunks:
                if len(chunk.strip()) < 50:  # Skip very short chunks
                    continue
                    
                chunk_summary = summarizer(
                    chunk, 
                    max_length=min(max_length, len(chunk.split()) // 2), 
                    min_length=min(min_length, len(chunk.split()) // 4),
                    do_sample=False
                )
                summaries.append(chunk_summary[0]["summary_text"])
            
            # Combine summaries and format as bullet points
            combined_notes = "\n".join([f"• {summary}" for summary in summaries])
            return combined_notes
        
        else:
            # For shorter texts, process directly
            summary = summarizer(
                text, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )
            
            # Format as bullet points
            summary_text = summary[0]["summary_text"]
            # Split by sentences and format as bullet points
            sentences = [s.strip() for s in summary_text.split('.') if s.strip()]
            bullet_notes = "\n".join([f"• {sentence}." for sentence in sentences])
            
            return bullet_notes
            
    except Exception as e:
        # Fallback to simple summarizer if AI model fails
        print(f"AI summarization failed, using fallback: {e}")
        return simple_text_summarizer(text)
