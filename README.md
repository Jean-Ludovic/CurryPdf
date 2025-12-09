# QR Code Generator & PDF Exporter

A simple Streamlit app that converts any link into a QR code, allows you to add and edit text, and export everything as a PDF.

## Features

- 🔗 **Link to QR Code**: Convert any URL/link into a QR code
- 📝 **Text Editing**: Add and edit text that will be included in the PDF
- 📥 **Download Options**: Download QR code as PNG or JPG
- 📄 **PDF Export**: Generate a PDF document with the QR code, link, text, and timestamp

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. The app will open in your default web browser.

3. To use the app:
   - Enter a link/URL in the input field
   - Click "Generate QR Code"
   - Optionally add/edit text in the text area
   - Download the QR code as PNG or JPG
   - Download everything as a PDF document

## Customization

The app includes a sidebar with settings to customize:
- QR Code size (100-500 pixels)
- QR Code border (1-10)
- Error correction level (LOW, MEDIUM, QUARTILE, HIGH)

## Requirements

- Python 3.7+
- streamlit
- qrcode[pil]
- Pillow
- reportlab

