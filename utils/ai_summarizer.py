import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OfflineAISummarizer:
    """Offline AI summarizer using local transformers models"""
    
    def __init__(self):
        self.summarizer = None
        self.model_name = "facebook/bart-large-cnn"  # High quality model
        self.fallback_model = "sshleifer/distilbart-cnn-12-6"  # Smaller fallback
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the summarization model with fallback"""
        try:
            logger.info(f"Loading summarization model: {self.model_name}")
            self.summarizer = pipeline(
                "summarization",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            logger.info("Primary model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load primary model: {e}")
            try:
                logger.info(f"Loading fallback model: {self.fallback_model}")
                self.summarizer = pipeline(
                    "summarization",
                    model=self.fallback_model,
                    device=0 if self.device == "cuda" else -1
                )
                logger.info("Fallback model loaded successfully")
            except Exception as fallback_error:
                logger.error(f"Failed to load fallback model: {fallback_error}")
                self.summarizer = None
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """Summarize text using the loaded model"""
        if not self.summarizer:
            return self._simple_fallback_summary(text)
        
        try:
            # Clean and prepare text
            text = text.strip()
            if len(text) < 100:  # Too short to summarize
                return f"• {text}"
            
            # Split long texts into chunks
            chunks = self._split_text(text, max_chunk_size=1024)
            summaries = []
            
            for chunk in chunks:
                try:
                    result = self.summarizer(
                        chunk,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False,
                        truncation=True
                    )
                    summary = result[0]['summary_text']
                    summaries.append(summary)
                except Exception as chunk_error:
                    logger.warning(f"Error summarizing chunk: {chunk_error}")
                    # Fallback for this chunk
                    summaries.append(self._simple_fallback_summary(chunk))
            
            # Combine summaries and format as bullet points
            combined_summary = " ".join(summaries)
            return self._format_as_bullet_points(combined_summary)
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return self._simple_fallback_summary(text)
    
    def _split_text(self, text: str, max_chunk_size: int = 1024) -> list:
        """Split text into chunks suitable for the model"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    def _format_as_bullet_points(self, summary: str) -> str:
        """Format summary as bullet points"""
        sentences = summary.split('. ')
        bullet_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                # Remove trailing period if present
                if sentence.endswith('.'):
                    sentence = sentence[:-1]
                bullet_points.append(f"• {sentence}")
        
        return "\n".join(bullet_points) if bullet_points else f"• {summary}"
    
    def _simple_fallback_summary(self, text: str) -> str:
        """Simple fallback when AI models fail"""
        if not text or not text.strip():
            return "• No content provided"
        
        sentences = text.strip().split('.')
        if len(sentences) <= 3:
            return f"• {text.strip()}"
        
        # Take first, middle, and last sentences
        summary_sentences = [sentences[0], sentences[len(sentences)//2], sentences[-1]]
        bullet_points = []
        
        for sentence in summary_sentences:
            cleaned = sentence.strip()
            if cleaned and len(cleaned) > 10:
                bullet_points.append(f"• {cleaned}")
        
        return "\n".join(bullet_points) if bullet_points else f"• {text[:200]}..."

# Global instance
_ai_summarizer = None

def get_ai_summarizer() -> OfflineAISummarizer:
    """Get or create the global AI summarizer instance"""
    global _ai_summarizer
    if _ai_summarizer is None:
        _ai_summarizer = OfflineAISummarizer()
    return _ai_summarizer

def generate_notes_ai(text: str) -> str:
    """Generate notes using offline AI models"""
    summarizer = get_ai_summarizer()
    return summarizer.summarize_text(text)
