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
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 30, note_style: str = "structured") -> str:
        """Summarize text using the loaded model with different note styles"""
        if not self.summarizer:
            return self._create_structured_notes(text, use_ai=False, note_style=note_style)
        
        try:
            # Clean and prepare text
            text = text.strip()
            if len(text) < 100:  # Too short to summarize
                return self._format_short_content(text, note_style)
            
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
                    summaries.append(self._extract_key_sentences(chunk))
            
            # Create structured notes from summaries
            return self._create_structured_notes(" ".join(summaries), use_ai=True, note_style=note_style)
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return self._create_structured_notes(text, use_ai=False, note_style=note_style)
    
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
        """Format summary as bullet points (legacy method)"""
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
    
    def _create_structured_notes(self, text: str, use_ai: bool = True, note_style: str = "structured") -> str:
        """Create comprehensive structured notes from text"""
        if not text or not text.strip():
            return "**No Content Available**\n\n---\n\n*No text content was found in the document.*"
        
        if note_style == "bullet":
            return self._create_bullet_notes(text)
        elif note_style == "detailed":
            return self._create_detailed_analysis(text)
        else:  # structured (default)
            return self._create_standard_structured_notes(text, use_ai)
    
    def _create_bullet_notes(self, text: str) -> str:
        """Create simple bullet point notes"""
        sentences = text.split('. ')
        bullet_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 15:
                # Remove trailing period if present
                if sentence.endswith('.'):
                    sentence = sentence[:-1]
                bullet_points.append(f"• {sentence}")
        
        return "\n".join(bullet_points) if bullet_points else f"• {text}"
    
    def _create_detailed_analysis(self, text: str) -> str:
        """Create detailed analysis-style notes"""
        lines = []
        lines.append("# **DETAILED ANALYSIS**")
        lines.append("=" * 60)
        lines.append("")
        
        # Executive Summary
        lines.append("## **EXECUTIVE SUMMARY**")
        summary = self._create_executive_summary(text)
        lines.append(summary)
        lines.append("")
        
        # Content Analysis
        lines.append("## **CONTENT ANALYSIS**")
        key_points = self._extract_key_points(text)
        for i, point in enumerate(key_points, 1):
            lines.append(f"**{i}.** {point}")
        lines.append("")
        
        # Themes and Topics
        main_topics = self._identify_main_topics(text)
        if main_topics:
            lines.append("## **MAIN THEMES**")
            for topic in main_topics:
                lines.append(f"→ {topic}")
            lines.append("")
        
        # Detailed Breakdown
        lines.append("## **DETAILED BREAKDOWN**")
        paragraphs = text.split('\n')
        for i, para in enumerate(paragraphs[:5], 1):  # Limit to 5 paragraphs
            if para.strip():
                lines.append(f"**Section {i}:**")
                lines.append(para.strip())
                lines.append("")
        
        # Key Insights
        lines.append("## **KEY INSIGHTS**")
        insights = self._extract_insights(text)
        for insight in insights:
            lines.append(f"✓ {insight}")
        lines.append("")
        
        # Conclusion
        lines.append("## **CONCLUSION**")
        conclusion = self._create_conclusion(text)
        lines.append(conclusion)
        lines.append("")
        
        lines.append("---")
        lines.append("*Detailed analysis generated by AutoNote AI*")
        
        return "\n".join(lines)
    
    def _create_standard_structured_notes(self, text: str, use_ai: bool = True) -> str:
        """Create standard structured notes"""
        # Extract key information
        key_points = self._extract_key_points(text)
        main_topics = self._identify_main_topics(text)
        
        # Build structured notes
        notes = []
        notes.append("# **STUDY NOTES**")
        notes.append("=" * 50)
        notes.append("")
        
        # Overview section
        if len(text) > 200:
            overview = self._create_overview(text)
            notes.append("## **OVERVIEW**")
            notes.append(overview)
            notes.append("")
        
        # Main topics section
        if main_topics:
            notes.append("## **KEY TOPICS**")
            for i, topic in enumerate(main_topics, 1):
                notes.append(f"**{i}.** {topic}")
            notes.append("")
        
        # Detailed points section
        notes.append("## **IMPORTANT POINTS**")
        for point in key_points:
            notes.append(f"• {point}")
        notes.append("")
        
        # Summary section
        summary = self._create_executive_summary(text)
        notes.append("## **SUMMARY**")
        notes.append(summary)
        notes.append("")
        
        # Study tips
        notes.append("## **STUDY RECOMMENDATIONS**")
        notes.append("• Review the key topics regularly")
        notes.append("• Focus on understanding the main concepts")
        notes.append("• Create your own examples for better retention")
        notes.append("")
        
        notes.append("---")
        notes.append("*Generated by AutoNote AI*")
        
        return "\n".join(notes)
    
    def _extract_insights(self, text: str) -> list:
        """Extract key insights from text"""
        sentences = text.split('.')
        insights = []
        
        # Look for insight indicators
        insight_words = ['shows', 'demonstrates', 'reveals', 'indicates', 'suggests', 'implies', 'proves']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(word in sentence.lower() for word in insight_words) and len(sentence) > 30:
                insights.append(sentence)
        
        # If no insights found, extract meaningful conclusions
        if not insights:
            meaningful_sentences = [s.strip() for s in sentences if 40 <= len(s.strip()) <= 150]
            insights = meaningful_sentences[:3]
        
        return insights[:5]  # Limit to 5 insights
    
    def _create_conclusion(self, text: str) -> str:
        """Create a conclusion from the text"""
        sentences = text.split('.')
        
        # Look for conclusion indicators
        conclusion_words = ['conclusion', 'summary', 'in summary', 'finally', 'therefore', 'thus']
        
        for sentence in sentences:
            if any(word in sentence.lower() for word in conclusion_words):
                return sentence.strip()
        
        # If no explicit conclusion, use the last meaningful sentence
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        if meaningful_sentences:
            return meaningful_sentences[-1]
        
        return "The content provides valuable information for further study and analysis."
    
    def _format_short_content(self, text: str, note_style: str) -> str:
        """Format short content appropriately"""
        cleaned_text = text.strip()
        
        if note_style == "bullet":
            return f"• {cleaned_text}"
        elif note_style == "structured":
            return f"## **Quick Note**\n\n{cleaned_text}\n\n---\n*Short content summary*"
        else:
            return cleaned_text
    
    def _extract_key_points(self, text: str) -> list:
        """Extract key points from text"""
        sentences = text.split('.')
        points = []
        
        # Look for important indicators
        important_words = ['important', 'key', 'significant', 'crucial', 'essential', 'main', 'primary', 'major']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:
                # Prioritize sentences with important keywords
                if any(word in sentence.lower() for word in important_words):
                    points.append(sentence)
                elif len(sentence) > 50 and len(sentence) < 200:
                    points.append(sentence)
        
        # If no good points found, use first few sentences
        if not points:
            points = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        return points[:8]  # Limit to 8 key points
    
    def _identify_main_topics(self, text: str) -> list:
        """Identify main topics from text"""
        # Simple topic extraction based on sentence structure
        sentences = text.split('.')
        topics = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for topic indicators
            if any(phrase in sentence.lower() for phrase in ['this chapter', 'this section', 'we discuss', 'focuses on', 'about']):
                # Extract the topic
                topic = sentence[:100] + "..." if len(sentence) > 100 else sentence
                topics.append(topic)
        
        # If no explicit topics found, create from key sentences
        if not topics and sentences:
            topics = [sentences[0][:80] + "..." if len(sentences[0]) > 80 else sentences[0]]
        
        return topics[:5]  # Limit to 5 main topics
    
    def _create_overview(self, text: str) -> str:
        """Create a brief overview of the content"""
        sentences = text.split('.')
        if len(sentences) >= 3:
            overview_parts = [sentences[0], sentences[len(sentences)//2], sentences[-2]]
            overview = ". ".join([s.strip() for s in overview_parts if s.strip()])
            return overview + "."
        else:
            return text[:300] + "..." if len(text) > 300 else text
    
    def _create_executive_summary(self, text: str) -> str:
        """Create an executive summary"""
        if len(text) < 200:
            return text
        
        # Take first and last portions for summary
        first_part = text[:len(text)//3]
        last_part = text[-len(text)//3:]
        
        summary = f"{first_part[:150]}... {last_part[-150:]}"
        return summary
    
    def _extract_key_sentences(self, text: str) -> str:
        """Extract key sentences when AI fails"""
        sentences = text.split('.')
        key_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if 30 <= len(sentence) <= 150:  # Good length sentences
                key_sentences.append(sentence)
        
        if not key_sentences:
            key_sentences = [text[:200]]
        
        return ". ".join(key_sentences[:3])
    
    def _simple_fallback_summary(self, text: str, note_style: str = "structured") -> str:
        """Enhanced fallback when AI models fail"""
        if not text or not text.strip():
            return "**No Content Available**\n\n---\n\n*No text content was found.*"
        
        # Use the structured notes method even for fallback
        return self._create_structured_notes(text, use_ai=False, note_style=note_style)

# Global instance
_ai_summarizer = None

def get_ai_summarizer() -> OfflineAISummarizer:
    """Get or create the global AI summarizer instance"""
    global _ai_summarizer
    if _ai_summarizer is None:
        _ai_summarizer = OfflineAISummarizer()
    return _ai_summarizer

def generate_notes_ai(text: str, note_style: str = "structured") -> str:
    """Generate comprehensive notes using offline AI models"""
    summarizer = get_ai_summarizer()
    return summarizer.summarize_text(text, note_style=note_style)
