# autonote

A production-ready Flask web application that transforms documents into structured bullet-point notes using AI-powered summarization.

## Features

- **Multi-format input support**: Text, PDF, DOCX, and image files (PNG/JPG with OCR)
- **AI-powered summarization**: Uses Hugging Face transformers for intelligent note generation
- **Multiple export formats**: Download notes as TXT, MD, PDF, or DOCX
- **Rate limiting**: 100 requests per day, 10 per minute
- **Responsive design**: Clean, modern UI with Tailwind CSS
- **Docker ready**: Easy deployment with Docker containerization

## Supported File Types

- **Text**: Direct text input via textarea
- **PDF**: Extracting text from PDF documents
- **DOCX**: Microsoft Word document processing
- **Images**: PNG/JPG files with OCR text extraction
- **TXT**: Plain text file upload

## Installation

### Local Development

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

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t autonote .
```

2. Run the container:
```bash
docker run -p 8000:8000 autonote
```

## Configuration

Environment variables in `.env`:

- `SECRET_KEY`: Flask secret key for sessions
- `MODEL_NAME`: Hugging Face model name (default: sshleifer/distilbart-cnn-12-6)

## Project Structure

```
autonote/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env                  # Environment variables
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   └── result.html       # Results page
├── static/               # Static assets
│   ├── css/
│   └── js/
├── utils/                # Utility modules
│   ├── ocr.py           # Image OCR processing
│   ├── pdf_reader.py    # PDF text extraction
│   ├── docx_reader.py   # DOCX text extraction
│   ├── summarizer.py    # AI summarization
│   └── file_exports.py  # Export utilities
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
- **transformers**: AI summarization models
- **pytesseract**: OCR for images
- **PyMuPDF**: PDF text extraction
- **python-docx**: DOCX processing
- **reportlab**: PDF generation
- **Pillow**: Image processing

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
