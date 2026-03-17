import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
import logging
import os

class UPIFraudDetector:
    def __init__(self, tesseract_path=None):
        self.fraud_indicators = []
        self.confidence_score = 100
        
        # Set Tesseract path from environment variable
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logging.info(f"Tesseract path set to: {tesseract_path}")
        
        # Verify Tesseract is accessible
        try:
            version = pytesseract.get_tesseract_version()
            logging.info(f"Tesseract version: {version}")
        except Exception as e:
            logging.warning(f"Tesseract not available: {e}")
    
    def analyze_text_consistency(self, img):
        """Extract and analyze text for inconsistencies"""
        try:
            # Extract text using OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            
            # Check for UPI patterns
            upi_patterns = [
                r'UPI|PhonePe|Google Pay|Paytm|BHIM',
                r'₹\s*\d+[,.]?\d*',
                r'[A-Z]{4}0\d{13}',
                r'Transaction\s+(ID|Ref)',
                r'Success|Failed|Pending'
            ]
            
            found_patterns = 0
            for pattern in upi_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found_patterns += 1
            
            if found_patterns < 2:
                self.fraud_indicators.append({
                    "type": "Missing UPI Elements",
                    "severity": "high",
                    "description": "Expected UPI transaction elements not found"
                })
                self.confidence_score -= 25
                
        except pytesseract.TesseractNotFoundError:
            logging.error("Tesseract not found. Please set TESSERACT_PATH environment variable.")
            self.fraud_indicators.append({
                "type": "OCR Error",
                "severity": "high",
                "description": "OCR system unavailable - text analysis skipped"
            })
            self.confidence_score -= 15
        except Exception as e:
            logging.error(f"Error in text analysis: {e}")
