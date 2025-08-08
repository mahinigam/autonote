from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import markdown
from config import Config
from utils.pdf_reader import pdf_to_text
from utils.docx_reader import docx_to_text
from utils.summarizer import generate_notes
from utils.file_exports import save_as_txt, save_as_md, save_as_pdf, save_as_docx
from utils.cleanup import start_background_cleanup
from utils.chatbot import chat_with_document, get_chatbot

app = Flask(__name__)
app.config.from_object(Config)

# Initialize configuration
Config.init_app(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day"]
)

# Ensure downloads directory exists
os.makedirs(app.config['UPLOAD_PATH'], exist_ok=True)

# Start background cleanup for old files
start_background_cleanup(app.config['UPLOAD_PATH'], interval_hours=1)

# Initialize Online AI service
print("AutoNote configured for online AI services")
if os.getenv('GEMINI_API_KEY'):
    print("Google Gemini API configured - all AI features available")
else:
    print("GEMINI_API_KEY not found - AI features will use fallback mode")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in [ext.lstrip('.') for ext in app.config['UPLOAD_EXTENSIONS']]

def extract_text_from_file(file_path, file_extension):
    """Extract text from uploaded file based on its extension"""
    try:
        if file_extension == '.pdf':
            return pdf_to_text(file_path)
        elif file_extension == '.docx':
            return docx_to_text(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return ""
    except Exception as e:
        flash(f"Error extracting text from file: {str(e)}", "error")
        return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        from utils.online_ai import get_online_ai
        online_ai = get_online_ai()
        ai_status = "ready" if online_ai.is_initialized else "fallback"
    except Exception:
        ai_status = "fallback"
    
    return jsonify({
        "status": "healthy", 
        "service": "autonote",
        "ai_status": ai_status,
        "features": {
            "online_ai": True,
            "pdf_processing": True,
            "docx_processing": True,
            "cloud_powered": True
        }
    }), 200

@app.route('/process', methods=['POST'])
@limiter.limit("10 per minute")
def process():
    extracted_text = ""
    
    # Get text from textarea
    user_text = request.form.get('text', '').strip()
    if user_text:
        extracted_text += user_text + "\n\n"
    
    # Process uploaded file
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_extension = '.' + filename.rsplit('.', 1)[1].lower()
                
                # Save uploaded file temporarily
                temp_path = os.path.join(app.config['UPLOAD_PATH'], f"temp_{uuid.uuid4()}_{filename}")
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                file.save(temp_path)
                
                # Extract text from file
                file_text = extract_text_from_file(temp_path, file_extension)
                if file_text:
                    extracted_text += file_text
                
                # Clean up temporary file
                try:
                    os.remove(temp_path)
                except Exception as cleanup_error:
                    print(f"Warning: Could not remove temp file {temp_path}: {cleanup_error}")
                    
            except Exception as file_error:
                flash(f"Error processing uploaded file: {str(file_error)}", "error")
                return redirect(url_for('index'))
        elif file and file.filename and not allowed_file(file.filename):
            flash("File type not supported. Please upload TXT, PDF, or DOCX files.", "error")
            return redirect(url_for('index'))
    
    if not extracted_text.strip():
        flash("Please provide text or upload a file.", "error")
        return redirect(url_for('index'))
    
    # Generate notes using summarization
    try:
        # Get note style from form, default to structured
        note_style = request.form.get('note_style', 'structured')
        notes = generate_notes(extracted_text, note_style=note_style)
        
        # Generate unique file ID for downloads
        file_id = str(uuid.uuid4())
        
        # Save notes in different formats
        save_as_txt(notes, file_id, app.config['UPLOAD_PATH'])
        save_as_md(notes, file_id, app.config['UPLOAD_PATH'])
        save_as_pdf(notes, file_id, app.config['UPLOAD_PATH'])
        save_as_docx(notes, file_id, app.config['UPLOAD_PATH'])
        
        # Convert markdown notes to HTML for better display
        notes_html = markdown.markdown(notes)
        
        # Set up chatbot with the source document
        chatbot = get_chatbot()
        chatbot.set_source_document(extracted_text)
        suggestions = chatbot.get_suggestions()
        
        return render_template('result.html', 
                             notes=notes,
                             notes_html=notes_html, 
                             original_text=extracted_text,
                             chat_suggestions=suggestions,
                             file_id=file_id)
    
    except Exception as e:
        flash(f"Error generating notes: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/download/<file_id>')
def download(file_id):
    format_type = request.args.get('format', 'txt')
    filename = f"{file_id}.{format_type}"
    filepath = os.path.join(app.config['UPLOAD_PATH'], filename)
    
    if os.path.exists(filepath):
        return send_from_directory(app.config['UPLOAD_PATH'], filename, as_attachment=True)
    else:
        flash("File not found.", "error")
        return redirect(url_for('index'))

@app.route('/api/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat_api():
    """API endpoint for chatbot interactions"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get the chatbot response
        response = chat_with_document(question)
        
        return jsonify({
            'response': response,
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Chat error: {str(e)}',
            'success': False
        }), 500

@app.route('/api/chat/suggestions')
@limiter.limit("10 per minute")
def chat_suggestions():
    """Get conversation suggestions"""
    try:
        chatbot = get_chatbot()
        suggestions = chatbot.get_suggestions()
        
        return jsonify({
            'suggestions': suggestions,
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Error getting suggestions: {str(e)}',
            'success': False
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
