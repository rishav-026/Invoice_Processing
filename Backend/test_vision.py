from google.cloud import vision
import os

# Correct way to get the environment variable
print("GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

try:
    # Initialize Google Vision API Client
    client = vision.ImageAnnotatorClient()
    print("✅ Google Vision API is set up correctly!")
except Exception as e:
    print("❌ Error initializing Google Vision API:", str(e))
