# Invoice Processing Tool Documentation

## Overview
The **Invoice Processing Tool** is a web-based application designed to automate the extraction of information from invoice images. It supports both typed and handwritten invoices through the use of Tesseract OCR (local) and Google Cloud Vision API (cloud). The extracted data includes invoice number, date, vendor details, customer information, item breakdown, and totals.

The tool consists of:
- **Flask API** backend for OCR and parsing logic
- **React.js** frontend for user interaction

---

## Table of Contents
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Setup](#setup)
5. [Running the Application](#running-the-application)
6. [API Endpoints](#api-endpoints)
7. [Example Usage](#example-usage)
8. [Additional Scripts](#additional-scripts)
9. [License](#license)
10. [Acknowledgements](#acknowledgements)

---

## Features

### Text Extraction
- Extracts raw text using **Tesseract OCR** or **Google Cloud Vision API**

### Invoice Parsing
- Extracts and identifies fields:
  - Invoice Number
  - Date
  - Vendor and Customer Names/Addresses
  - Item List
  - Subtotal, Tax, Total

### File Upload
- Upload invoices via frontend

### CORS Support
- Allows cross-origin requests from the React.js frontend

### Error Handling
- Falls back to Tesseract OCR if Google Vision fails

---

## Technologies Used
- **Python 3.7+** - Backend logic
- **Flask** - API development
- **Tesseract OCR** - Local OCR engine
- **Google Cloud Vision API** - Cloud OCR engine
- **React.js** - Frontend framework
- **Flask-CORS** - CORS middleware for Flask
- **Werkzeug** - File upload handling

---

## Project Structure

```
Invoice_Processing/
├── Backend/             # Flask API backend
│   ├── app.py           # Main entry point for Flask app
│   ├── test_vision.py   # Script to test Vision API
│   ├── test.http        # Optional HTTP request testing file
│   └── train_donut.py   # Document-understanding model trainer
├── Frontend/            # React frontend
│   ├── node_modules/    # React dependencies
│   ├── src/             # Frontend source files
│   └── README.md        # Frontend documentation
├── public/              # Static assets (images, etc.)
├── results/             # Output results and parsed data
├── src/                 # Shared or top-level source files
├── uploads/             # Uploaded invoice images
├── .env/                # Virtual environment (should be gitignored)
├── .gitignore
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
├── package-lock.json
├── postcss.config.js
└── .gitattributes
```

---

## Installation

### Prerequisites
- Python 3.7 or higher
- Tesseract OCR installed and accessible via PATH
- Google Cloud Platform account (for Vision API)
- Flask and other required Python packages

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/invoice-processing-tool.git
cd invoice-processing-tool
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:
- **Windows**: Download from [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract), add to system PATH
- **Linux**:
```bash
sudo apt install tesseract-ocr
```

4. Setup Google Vision API:
   - Create a GCP project
   - Enable Vision API
   - Download service account key JSON
   - Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

5. Create an `uploads` directory:
```bash
mkdir uploads
```

---

## Running the Application
### Start Flask Backend:
```bash
cd Backend
python app.py
```
Runs on: [http://localhost:5000](http://localhost:5000)

### Start React Frontend:
```bash
cd Frontend
npm install
npm start
```
Runs on: [http://localhost:3000](http://localhost:3000)

---

## API Endpoints

### `GET /`
- Renders a basic landing HTML page

### `POST /process-invoice`
- Accepts: Form-data with key `invoice` (image file)
- Returns: JSON with raw extracted text

#### Example Request:
```
invoice=<image-file>
```

#### Example Response:
```json
{
  "raw_text": "Extracted text from the invoice"
}
```

---

## Example Usage
1. Upload invoice via frontend form
2. Backend uses OCR (Vision API → Tesseract fallback)
3. Text is parsed and returned as structured JSON

### Example Raw Text Output:
```
Invoice No: INV123456
Date: 2025-04-30
Vendor: Example Vendor Inc.
Customer: John Doe
Items:
- Item 1: $100.00
- Item 2: $50.00
Subtotal: $150.00
Tax: $15.00
Total Amount: $165.00
```

---

## Additional Scripts

- `train_donut.py`: Used for training a document-understanding model (Donut). Useful if you want to improve accuracy beyond default OCR methods.
- `test_vision.py`: Quick script to validate Google Vision API results.
- `test.http`: Optional file for testing HTTP requests to the Flask API.

---

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

## Acknowledgements
- **Tesseract OCR** - [GitHub](https://github.com/tesseract-ocr/tesseract)
- **Google Cloud Vision API** - [Documentation](https://cloud.google.com/vision)
- **Flask** - [Official Docs](https://flask.palletsprojects.com/)
- **Werkzeug** - [Documentation](https://werkzeug.palletsprojects.com/)

---
