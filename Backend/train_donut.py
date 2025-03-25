from flask import Flask, request, jsonify, render_template
import os
import re
import json
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from google.cloud import vision

app = Flask(_name_)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

    # Preprocess Image for better OCR
    processed_image = preprocess_image(filepath)

    # Extract text using OCR (Google Vision API)
    extracted_data = extract_invoice_data(processed_image)

    # Debugging: Check extracted JSON
    print("Extracted JSON Data:", json.dumps(extracted_data, indent=4))

    return jsonify(extracted_data)

def preprocess_image(image_path):
    """Preprocess image to enhance OCR accuracy."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Resize for better recognition
    image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # Apply Adaptive Thresholding (for handwritten text)
    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Remove noise
    image = cv2.fastNlMeansDenoising(image, None, 30, 7, 21)

    # Save processed image
    processed_path = image_path.replace(".jpg", "_processed.jpg")
    cv2.imwrite(processed_path, image)

    return processed_path

def extract_invoice_data(image_path):
    """Extract text from the invoice using Google Vision API with improved structure."""
    try:
        client = vision.ImageAnnotatorClient()
        with open(image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.error.message:
            print(f"Google Vision API Error: {response.error.message}")
            raise Exception(response.error.message)

        # Extract text & bounding box data
        text_data = response.full_text_annotation.text
        words = response.text_annotations

        print("Extracted Text:\n", text_data)

    except Exception as e:
        print(f"Google Vision API failed: {e}")
        raise e

    return parse_invoice_text(words)

def parse_invoice_text(words):
    """Extract structured invoice data using bounding box position & regex."""
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

    extracted_lines = [word.description for word in words]

    for line in extracted_lines:
        line = line.strip()

        # Extract Invoice Number
        if not data['invoice_number']:
            match = re.search(r'(?:Invoice|Bill|Receipt)\s*(?:No\.?|#|ID)?:?\s*([\w-]+)', line, re.IGNORECASE)
            if match:
                data['invoice_number'] = match.group(1)

        # Extract Date
        if not data['date']:
            match = re.search(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b', line)
            if match:
                data['date'] = match.group(1)

        # Extract Total Amount
        if not data['total_amount']:
            match = re.search(r'(Total\s*(?:Amount)?\s*[:$]?\s*)([0-9,.]+)', line, re.IGNORECASE)
            if match:
                data['total_amount'] = match.group(2).replace(',', '')

        # Extract Subtotal
        if not data['subtotal']:
            match = re.search(r'(Sub\s*Total\s*[:$]?\s*)([0-9,.]+)', line, re.IGNORECASE)
            if match:
                data['subtotal'] = match.group(2).replace(',', '')

        # Extract Tax
        if not data['tax']:
            match = re.search(r'(Tax\s*(?:Amount)?\s*[:$]?\s*)([0-9,.]+)', line, re.IGNORECASE)
            if match:
                data['tax'] = match.group(2).replace(',', '')

        # Extract Vendor & Customer Name
        vendor_match = re.search(r'^(Vendor|Supplier|Seller):?\s*(.*)', line, re.IGNORECASE)
        customer_match = re.search(r'^(Customer|Client|Buyer):?\s*(.*)', line, re.IGNORECASE)

        if vendor_match:
            data['vendor_name'] = vendor_match.group(2).strip()
        if customer_match:
            data['customer_name'] = customer_match.group(2).strip()

        # Extract Address
        if "Address:" in line:
            address_match = re.search(r'Address:\s*(.+)', line, re.IGNORECASE)
            if address_match:
                if not data['vendor_address']:
                    data['vendor_address'] = address_match.group(1)
                else:
                    data['customer_address'] = address_match.group(1)

        # Extract Items with quantity & price
        item_match = re.search(r'^(.+?)\s+(\d+)\s+[x@]\s*\$?\s*([0-9,.]+)$', line, re.IGNORECASE)
        if item_match:
            description, quantity, price = item_match.groups()
            data['items'].append({
                'description': description.strip(),
                'quantity': int(quantity),
                'unit_price': float(price.replace(',', ''))
            })

    return data

if _name_ == '_main_':
    app.run(debug=True, port=8000, host='0.0.0.0')