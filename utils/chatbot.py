import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from typing import Optional, List, Dict, Union, Any
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentChatbot:
    """Interactive chatbot for document-based Q&A and content manipulation"""
    
    def __init__(self):
        self.qa_pipeline = None
        self.text_generator = None
        self.model_name = "microsoft/DialoGPT-medium"  # Conversational model
        self.qa_model_name = "deepset/roberta-base-squad2"  # Q&A model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.conversation_history = []
        self.source_document = ""
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the chatbot models with fallback"""
        try:
            logger.info("Loading chatbot models...")
            
            # Initialize Q&A pipeline for document questions
            self.qa_pipeline = pipeline(
                "question-answering",
                model=self.qa_model_name,
                device=0 if self.device == "cuda" else -1
            )
            
            # Initialize text generation for creative tasks
            self.text_generator = pipeline(
                "text-generation",
                model=self.model_name,
                device=0 if self.device == "cuda" else -1,
                pad_token_id=50256
            )
            
            logger.info("Chatbot models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load chatbot models: {e}")
            self.qa_pipeline = None
            self.text_generator = None
    
    def set_source_document(self, document_text: str):
        """Set the source document for the chatbot to reference"""
        self.source_document = document_text
        self.conversation_history = []
    
    def answer_question(self, question: str) -> str:
        """Answer questions about the source document"""
        if not self.source_document:
            return "No source document available. Please provide a document first."
        
        # Detect question type and route accordingly
        if self._is_table_request(question):
            return self._create_table_from_text(question)
        elif self._is_summary_request(question):
            return self._create_custom_summary(question)
        elif self._is_list_request(question):
            return self._create_list_from_text(question)
        else:
            return self._answer_direct_question(question)
    
    def _answer_direct_question(self, question: str) -> str:
        """Answer direct questions using Q&A model"""
        if not self.qa_pipeline:
            return self._fallback_answer(question)
        
        try:
            # Limit context length for better performance
            context = self.source_document[:2000] if len(self.source_document) > 2000 else self.source_document
            
            result = self.qa_pipeline(question=question, context=context)
            
            # Handle the result properly - it should be a dictionary
            if isinstance(result, dict) and 'score' in result and 'answer' in result:
                confidence = result['score']
                
                if confidence > 0.3:
                    answer = result['answer']
                    return f"**Answer:** {answer}\n\n*Confidence: {confidence:.2%}*"
                else:
                    return self._fallback_answer(question)
            else:
                return self._fallback_answer(question)
                
        except Exception as e:
            logger.error(f"Q&A error: {e}")
            return self._fallback_answer(question)
    
    def _is_table_request(self, question: str) -> bool:
        """Check if user is requesting a table"""
        table_keywords = ['table', 'chart', 'organize', 'tabulate', 'columns', 'rows']
        return any(keyword in question.lower() for keyword in table_keywords)
    
    def _is_summary_request(self, question: str) -> bool:
        """Check if user is requesting a summary"""
        summary_keywords = ['summarize', 'summary', 'brief', 'overview', 'main points']
        return any(keyword in question.lower() for keyword in summary_keywords)
    
    def _is_list_request(self, question: str) -> bool:
        """Check if user is requesting a list"""
        list_keywords = ['list', 'bullet points', 'enumerate', 'items', 'steps']
        return any(keyword in question.lower() for keyword in list_keywords)
    
    def _create_table_from_text(self, request: str) -> str:
        """Create a table from available information"""
        # Extract key information from the document
        sentences = self.source_document.split('.')
        data_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(word in sentence.lower() for word in ['is', 'are', 'has', 'have', 'contains']):
                data_points.append(sentence)
        
        if not data_points:
            return "I couldn't find enough structured data to create a meaningful table from the source document."
        
        # Create a simple table
        table = "| **Topic** | **Information** |\n"
        table += "|-----------|----------------|\n"
        
        for i, point in enumerate(data_points[:10], 1):  # Limit to 10 rows
            topic = f"Point {i}"
            info = point[:100] + "..." if len(point) > 100 else point
            table += f"| {topic} | {info} |\n"
        
        return f"**Generated Table:**\n\n{table}\n\n*Table created from available information in the source document.*"
    
    def _create_custom_summary(self, request: str) -> str:
        """Create a custom summary based on the request"""
        sentences = self.source_document.split('.')
        
        # Extract key sentences
        key_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if 30 <= len(sentence) <= 200:
                key_sentences.append(sentence)
        
        if len(key_sentences) < 3:
            return "The document is too short for a meaningful summary."
        
        # Create summary
        summary = "**Custom Summary:**\n\n"
        summary += f"• {key_sentences[0]}\n"
        summary += f"• {key_sentences[len(key_sentences)//2]}\n"
        summary += f"• {key_sentences[-1]}\n\n"
        summary += "*Summary generated based on your request.*"
        
        return summary
    
    def _create_list_from_text(self, request: str) -> str:
        """Create a list from the document content"""
        sentences = self.source_document.split('.')
        items = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 150:
                items.append(sentence)
        
        if not items:
            return "I couldn't extract meaningful list items from the source document."
        
        result = "**Generated List:**\n\n"
        for i, item in enumerate(items[:8], 1):  # Limit to 8 items
            result += f"{i}. {item}\n"
        
        result += "\n*List created from source document content.*"
        return result
    
    def _fallback_answer(self, question: str) -> str:
        """Fallback answer when AI models fail"""
        # Simple keyword-based responses
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['what', 'explain', 'describe']):
            # Find relevant sentences
            sentences = self.source_document.split('.')
            relevant = []
            
            question_words = question_lower.split()
            for sentence in sentences:
                if any(word in sentence.lower() for word in question_words if len(word) > 3):
                    relevant.append(sentence.strip())
            
            if relevant:
                return f"**Based on the document:** {relevant[0][:200]}..."
            else:
                return "I couldn't find specific information about that in the source document."
        
        elif any(word in question_lower for word in ['how many', 'count']):
            sentences = len(self.source_document.split('.'))
            words = len(self.source_document.split())
            return f"**Document Statistics:**\n• Sentences: {sentences}\n• Words: {words}\n• Characters: {len(self.source_document)}"
        
        else:
            return "I'm here to help you with questions about the source document. Try asking about specific topics mentioned in the text."
    
    def get_suggestions(self) -> List[str]:
        """Get conversation starter suggestions based on the document"""
        if not self.source_document:
            return ["Upload a document first to start chatting!"]
        
        suggestions = [
            "What are the main topics in this document?",
            "Can you create a table from this information?",
            "Summarize the key points for me",
            "What are the most important facts?",
            "Create a numbered list of main ideas"
        ]
        
        return suggestions

# Global chatbot instance
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
