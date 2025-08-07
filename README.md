# autonote

A production-ready Flask web application that transforms documents into structured bullet-point notes using AI-powered summarization.

## Features

- **Multi-format input support**: Text, PDF, DOCX, and image files (PNG/JPG with OCR)
- **AI-powered summarization**: Uses OpenAI API for intelligent note generation (with fallback)
- **Multiple export formats**: Download notes as TXT, MD, PDF, or DOCX
- **Rate limiting**: 100 requests per day, 10 per minute
- **Responsive design**: Clean, modern UI with Tailwind CSS
- **Cloud ready**: Optimized for Render deployment

## Supported File Types

- **Text**: Direct text input via textarea
- **PDF**: Extracting text from PDF documents
- **DOCX**: Microsoft Word document processing
- **Images**: PNG/JPG files with OCR text extraction
- **TXT**: Plain text file upload

## Deployment on Render

1. Fork this repository
2. Connect your GitHub repository to Render
3. Use the following settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Set environment variables in Render dashboard:
   - `SECRET_KEY`: Generate a secure secret key
   - `FLASK_ENV`: Set to `production`
   - `OPENAI_API_KEY`: (Optional) Your OpenAI API key for better summaries

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/mahinigam/autonote.git
cd autonote
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Configuration

Environment variables:

- `SECRET_KEY`: Flask secret key for sessions (auto-generated on Render)
- `FLASK_ENV`: Set to `production` for deployment
- `OPENAI_API_KEY`: (Optional) OpenAI API key for enhanced AI summaries

## Project Structure

```
autonote/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── runtime.txt           # Python version specification
├── .env.example          # Environment variables template
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   └── result.html       # Results page
├── static/               # Static assets
│   ├── css/logo.css      # Logo styling
│   └── images/           # Images
├── utils/                # Utility modules
│   ├── ocr.py           # Image OCR processing
│   ├── pdf_reader.py    # PDF text extraction
│   ├── docx_reader.py   # DOCX text extraction
│   ├── summarizer.py    # AI summarization
│   ├── file_exports.py  # Export utilities
│   └── cleanup.py       # Background cleanup
└── downloads/           # Temporary file storage
```

## Usage

1. **Text Input**: Paste text directly into the textarea
2. **File Upload**: Upload PDF, DOCX, TXT, or image files (max 10MB)
3. **Generate Notes**: Click "Generate Notes" to create structured bullet points
4. **Download**: Choose from TXT, MD, PDF, or DOCX export formats

## Dependencies

- **Flask**: Web framework
- **Flask-Limiter**: Rate limiting
- **OpenAI API**: AI summarization (optional)
- **pytesseract**: OCR for images
- **PyMuPDF**: PDF text extraction
- **python-docx**: DOCX processing
- **reportlab**: PDF generation
- **Pillow**: Image processing
- **gunicorn**: WSGI server for production

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Formatting

```bash
black .
flake8 .
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and commit: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Create Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please create an issue on GitHub.
