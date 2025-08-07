import os
from .online_ai import get_online_ai, chat_with_document_online
from typing import Optional, List, Dict, Union, Any
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentChatbot:
    """Interactive chatbot for document-based Q&A using online AI"""
    
    def __init__(self):
        self.source_document = ""
        self.online_ai = get_online_ai()
        logger.info("DocumentChatbot initialized with online AI")
    
    def set_source_document(self, document_text: str):
        """Set the source document for Q&A"""
        self.source_document = document_text
        logger.info(f"Document set ({len(document_text)} characters)")
    
    def answer_question(self, question: str) -> str:
        """Answer questions about the document using online AI"""
        if not self.source_document:
            return "No document loaded. Please upload a document first to ask questions about it."
        
        if not question or not question.strip():
            return "Please ask a specific question about the document, and I'll help you find the answer."
        
        # Check for special commands
        if self._is_table_request(question):
            return self._generate_table(question)
        elif self._is_list_request(question):
            return self._generate_list(question)
        
        # Use online AI for Q&A
        try:
            context = self.source_document[:2000] if len(self.source_document) > 2000 else self.source_document
            response = self.online_ai.chat_response(question, context)
            return response
        except Exception as e:
            logger.error(f"Online AI Q&A error: {e}")
            return self._fallback_answer(question)
    
    def get_suggestions(self) -> List[str]:
        """Get conversation suggestions based on the document"""
        if not self.source_document:
            return [
                "Upload a document to get started",
                "What types of files can I upload?",
                "How does the AI analysis work?",
                "What can I ask about my documents?"
            ]
        
        try:
            return self.online_ai.get_suggestions(self.source_document)
        except Exception as e:
            logger.error(f"Suggestion generation error: {e}")
            return self._default_suggestions()
    
    def _is_table_request(self, question: str) -> bool:
        """Check if the user is requesting a table"""
        table_keywords = ['table', 'chart', 'organize', 'tabulate', 'compare', 'matrix']
        return any(keyword in question.lower() for keyword in table_keywords)
    
    def _is_list_request(self, question: str) -> bool:
        """Check if the user is requesting a list"""
        list_keywords = ['list', 'bullet', 'points', 'items', 'enumerate', 'outline']
        return any(keyword in question.lower() for keyword in list_keywords)
    
    def _generate_table(self, question: str) -> str:
        """Generate a table based on the request"""
        try:
            table_prompt = f"""
            Based on this document and the user's request, create a well-formatted markdown table:
            
            Document: {self.source_document[:1000]}...
            
            User Request: {question}
            
            Create a clear, organized table that addresses their request. Use proper markdown table formatting.
            """
            
            response = self.online_ai.chat_response(table_prompt, self.source_document)
            return f"**Table Generated:**\n\n{response}"
        except Exception as e:
            logger.error(f"Table generation error: {e}")
            return "Sorry, I couldn't generate a table. Please try rephrasing your request or check the AI service connection."
    
    def _generate_list(self, question: str) -> str:
        """Generate a list based on the request"""
        try:
            list_prompt = f"""
            Based on this document and the user's request, create a well-formatted list:
            
            Document: {self.source_document[:1000]}...
            
            User Request: {question}
            
            Create a clear, organized list that addresses their request. Use bullet points or numbers as appropriate.
            """
            
            response = self.online_ai.chat_response(list_prompt, self.source_document)
            return f"**List Generated:**\n\n{response}"
        except Exception as e:
            logger.error(f"List generation error: {e}")
            return "Sorry, I couldn't generate a list. Please try rephrasing your request or check the AI service connection."
    
    def _fallback_answer(self, question: str) -> str:
        """Provide fallback response when AI is unavailable"""
        if 'summary' in question.lower() or 'summarize' in question.lower():
            # Basic summary from first few sentences
            sentences = self.source_document.split('.')[:3]
            summary = '. '.join(sentences).strip()
            return f"**Basic Summary:** {summary}...\n\n*(AI service unavailable - showing basic extraction)*"
        
        return """**AI Service Unavailable**
        
I'm currently unable to process your question due to AI service limitations. 

**What you can try:**
• Check your internet connection
• Verify API configuration  
• Try a simpler question
• Upload a smaller document

**Tip:** The AI service will be back online once the connection is restored."""
    
    def _default_suggestions(self) -> List[str]:
        """Default suggestions when AI is unavailable"""
        return [
            "What are the main topics covered?",
            "Can you summarize this document?",
            "List the key points",
            "Create a table of important information"
        ]


# Global instance
_document_chatbot = None

def get_chatbot() -> DocumentChatbot:
    """Get or create the global chatbot instance"""
    global _document_chatbot
    if _document_chatbot is None:
        _document_chatbot = DocumentChatbot()
    return _document_chatbot

def chat_with_document(question: str, document_text: Optional[str] = None) -> str:
    """Main function to chat with the document"""
    chatbot = get_chatbot()
    
    if document_text:
        chatbot.set_source_document(document_text)
    
    return chatbot.answer_question(question)
