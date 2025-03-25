from flask import Flask, request, jsonify, render_template
import os
import re
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from google.cloud import vision
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set Tesseract OCR Path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-invoice', methods=['POST'])
def process_invoice():
    if 'invoice' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['invoice']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Extract raw text only (skip structured data)
    extracted_data = extract_invoice_data(filepath)

    return jsonify({"raw_text": extracted_data["raw_text"]})  # ✅ Only send raw text


def extract_invoice_data(image_path):
    """Extracts text using Google Cloud Vision API or Tesseract OCR."""
    print(f"Processing image: {image_path}")

    try:
        client = vision.ImageAnnotatorClient()
        with open(image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.error.message:
            print(f"Google Vision API Error: {response.error.message}")
            return {"error": response.error.message}

        raw_text = response.full_text_annotation.text  # Raw extracted text
        print("Extracted text using Google Vision API")

    except Exception as e:
        print(f"Google Vision API failed. Using Tesseract OCR: {e}")
        raw_text = pytesseract.image_to_string(Image.open(image_path))

    print(f"Extracted Text:\n{raw_text}")
    
    # Parse the structured data
    structured_data = parse_invoice_text(raw_text)

    # Return both structured and raw extracted data
    return {
        "structured_data": structured_data,
        "raw_text": raw_text
    }

def parse_invoice_text(text):
    """Parses invoice text to extract structured data with improved accuracy."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    data = {
        'invoice_number': '',
        'date': '',
        'vendor_name': '',
        'vendor_address': '',
        'customer_name': '',
        'customer_address': '',
        'items': [],
        'subtotal': '',
        'tax': '',
        'total_amount': ''
    }

    # State tracking variables
    for line in lines:
        if not data['invoice_number']:
            invoice_match = re.search(r'(?:Invoice|Bill)\s*(?:No\.?|#|ID)?:?\s*(\w+)', line, re.IGNORECASE)
            if invoice_match:
                data['invoice_number'] = invoice_match.group(1)

        if not data['date']:
            date_match = re.search(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b', line)
            if date_match:
                data['date'] = date_match.group(1)

    return data

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')