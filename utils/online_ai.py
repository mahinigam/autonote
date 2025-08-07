"""
Online AI service using Google Gemini API
"""

import os
import logging
import google.generativeai as genai
from typing import Optional, List, Dict
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OnlineAI:
    """Online AI service using Google Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.is_initialized = False
        
        if self.api_key:
            self._initialize_gemini()
        else:
            logger.warning("GEMINI_API_KEY not found in environment variables")
    
    def _initialize_gemini(self):
        """Initialize Gemini API"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.is_initialized = True
            logger.info("Google Gemini API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self.is_initialized = False
    
    def generate_notes(self, text: str, note_type: str = "structured") -> str:
        """Generate notes using Gemini API"""
        if not self.is_initialized:
            return self._fallback_notes(text)
        
        try:
            # Create optimized prompts for different note types
            prompts = {
                "bullet": self._get_bullet_prompt(text),
                "detailed": self._get_detailed_prompt(text),
                "structured": self._get_structured_prompt(text)
            }
            
            prompt = prompts.get(note_type, prompts["structured"])
            
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                )
            )
            
            if response.text:
                logger.info(f"Generated {note_type} notes using Gemini API")
                return response.text
            else:
                logger.warning("Empty response from Gemini API")
                return self._fallback_notes(text)
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_notes(text)
    
    def chat_response(self, question: str, context: str = "") -> str:
        """Generate chatbot response using Gemini API"""
        if not self.is_initialized:
            return "I'm sorry, but the AI service is currently unavailable. Please check your API configuration and try again."
        
        try:
            prompt = self._get_chat_prompt(question, context)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                )
            )
            
            if response.text:
                logger.info("Generated chat response using Gemini API")
                return response.text
            else:
                return "I couldn't generate a response. Please try rephrasing your question."
                
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return f"I encountered an error: {str(e)}. Please try again in a moment."
    
    def get_suggestions(self, document_text: str = "") -> List[str]:
        """Generate conversation suggestions using Gemini API"""
        if not self.is_initialized:
            return self._default_suggestions()
        
        try:
            prompt = f"""
            Based on this document content, suggest 3-4 helpful questions a user might ask:
            
            Document: {document_text[:500]}...
            
            Generate practical questions like:
            - "What are the main topics?"
            - "Create a summary table"
            - "List key points"
            
            Return only the questions, one per line, without numbers or bullets.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=200,
                )
            )
            
            if response.text:
                suggestions = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
                return suggestions[:4]  # Limit to 4 suggestions
            else:
                return self._default_suggestions()
                
        except Exception as e:
            logger.error(f"Gemini suggestions error: {e}")
            return self._default_suggestions()
    
    def _get_structured_prompt(self, text: str) -> str:
        """Generate structured notes prompt"""
        return f"""
        Create comprehensive study notes from this content. Format as follows:

        # STUDY NOTES

        ## OVERVIEW
        [Brief overview in 2-3 sentences]

        ## KEY CONCEPTS
        [List main concepts with brief explanations]

        ## MAIN POINTS
        [Detailed points with explanations]

        ## IMPORTANT DETAILS
        [Additional important information]

        ## SUMMARY
        [Concise summary]

        Content to analyze:
        {text}

        Make the notes clear, well-organized, and study-friendly with proper markdown formatting.
        """
    
    def _get_detailed_prompt(self, text: str) -> str:
        """Generate detailed notes prompt"""
        return f"""
        Create detailed academic notes from this content:

        # DETAILED NOTES

        ## COMPREHENSIVE ANALYSIS
        [Thorough analysis with explanations]

        ## DETAILED BREAKDOWN
        [Point-by-point detailed breakdown]

        ## IN-DEPTH INSIGHTS
        [Deeper insights and implications]

        ## ADDITIONAL CONTEXT
        [Context and background information]

        Content to analyze:
        {text}

        Provide thorough, academic-level notes with comprehensive explanations.
        """
    
    def _get_bullet_prompt(self, text: str) -> str:
        """Generate bullet notes prompt"""
        return f"""
        Create concise bullet-point notes from this content:

        # QUICK NOTES

        ## Main Topics
        • [Key topic 1]
        • [Key topic 2]
        • [Key topic 3]

        ## Important Points
        • [Important point 1]
        • [Important point 2]
        • [Important point 3]

        ## Key Takeaways
        • [Takeaway 1]
        • [Takeaway 2]
        • [Takeaway 3]

        Content to analyze:
        {text}

        Keep it concise and easy to scan with clear bullet points.
        """
    
    def _get_chat_prompt(self, question: str, context: str) -> str:
        """Generate chat response prompt"""
        return f"""
        You are a helpful AI assistant for document analysis. Answer the user's question based on the provided context.

        Context: {context}

        User Question: {question}

        Instructions:
        - Provide helpful, accurate responses
        - If the question is about creating tables or lists, format them nicely
        - Use markdown formatting when appropriate
        - If you can't answer from the context, say so politely
        - Be conversational but informative

        Response:
        """
    
    def _fallback_notes(self, text: str) -> str:
        """Fallback notes when AI is unavailable"""
        lines = []
        lines.append("# STUDY NOTES")
        lines.append("*(Generated with basic processing - AI service unavailable)*")
        lines.append("")
        lines.append("## CONTENT OVERVIEW")
        
        # Basic text processing
        sentences = text.strip().split('.')
        word_count = len(text.split())
        
        lines.append(f"**Word Count:** {word_count}")
        lines.append(f"**Estimated Reading Time:** {word_count // 200 + 1} minutes")
        lines.append("")
        
        lines.append("## KEY CONTENT")
        if len(sentences) <= 5:
            for i, sentence in enumerate(sentences[:5], 1):
                if sentence.strip():
                    lines.append(f"{i}. {sentence.strip()}")
        else:
            # Take first few and last few sentences
            for i, sentence in enumerate(sentences[:3], 1):
                if sentence.strip():
                    lines.append(f"• {sentence.strip()}")
            
            if len(sentences) > 6:
                lines.append("• [... content continues ...]")
                
            for sentence in sentences[-2:]:
                if sentence.strip():
                    lines.append(f"• {sentence.strip()}")
        
        lines.append("")
        lines.append("## NOTE")
        lines.append("*AI service is currently unavailable. Please check your API configuration for enhanced note generation.*")
        
        return "\n".join(lines)
    
    def _default_suggestions(self) -> List[str]:
        """Default suggestions when AI is unavailable"""
        return [
            "What are the main topics covered?",
            "Can you create a summary?",
            "List the key points",
            "What should I remember from this?"
        ]


# Global instance
_online_ai = None

def get_online_ai() -> OnlineAI:
    """Get or create the global online AI instance"""
    global _online_ai
    if _online_ai is None:
        _online_ai = OnlineAI()
    return _online_ai

def generate_notes_online(text: str, note_type: str = "structured") -> str:
    """Main function to generate notes using online AI"""
    ai = get_online_ai()
    return ai.generate_notes(text, note_type)

def chat_with_document_online(question: str, context: str = "") -> str:
    """Main function to chat using online AI"""
    ai = get_online_ai()
    return ai.chat_response(question, context)
