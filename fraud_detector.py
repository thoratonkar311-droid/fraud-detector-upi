import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
from skimage.metrics import structural_similarity as ssim
import logging
from utils import check_image_metadata, detect_forgery_patterns

class UPIFraudDetector:
    def __init__(self):
        self.fraud_indicators = []
        self.confidence_score = 100
        
    def analyze(self, image):
        """Main analysis function"""
        self.fraud_indicators = []
        self.confidence_score = 100
        
        # Convert PIL to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Run all detection methods
        self.check_image_quality(img_cv)
        self.detect_screenshot_artifacts(img_cv)
        self.analyze_text_consistency(img_cv)
        self.detect_editing_traces(img_cv)
        self.check_upi_patterns(img_cv)
        
        # Calculate final confidence
        self.calculate_final_score()
        
        return {
            "is_fraudulent": self.confidence_score < 70,
            "confidence_score": self.confidence_score,
            "fraud_indicators": self.fraud_indicators,
            "analysis_summary": self.generate_summary()
        }
    
    def check_image_quality(self, img):
        """Check for basic image quality issues"""
        try:
            # Check resolution
            height, width = img.shape[:2]
            if width < 400 or height < 600:
                self.fraud_indicators.append({
                    "type": "Low Resolution",
                    "severity": "medium",
                    "description": "Image resolution is suspiciously low"
                })
                self.confidence_score -= 15
            
            # Check for compression artifacts
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:
                self.fraud_indicators.append({
                    "type": "Compression Artifacts",
                    "severity": "medium",
                    "description": "Signs of heavy compression detected"
                })
                self.confidence_score -= 10
                
        except Exception as e:
            logging.error(f"Error in image quality check: {e}")
    
    def detect_screenshot_artifacts(self, img):
        """Detect if this is a screenshot and check for tampering"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect screen capture patterns
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            if lines is not None:
                # Check for uniform lines that might indicate screenshot boundaries
                horizontal_lines = 0
                vertical_lines = 0
                
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                    
                    if angle < 10 or angle > 170:
                        horizontal_lines += 1
                    if 80 < angle < 100:
                        vertical_lines += 1
                
                if horizontal_lines > 10 and vertical_lines > 10:
                    self.fraud_indicators.append({
                        "type": "Screenshot Detection",
                        "severity": "low",
                        "description": "Image appears to be a screenshot"
                    })
                    self.confidence_score -= 5
                    
        except Exception as e:
            logging.error(f"Error in screenshot artifact detection: {e}")
    
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
                
        except Exception as e:
            logging.error(f"Error in text analysis: {e}")
    
    def detect_editing_traces(self, img):
        """Detect signs of image editing/manipulation"""
        try:
            # Error Level Analysis (ELA)
            quality = 90
            temp_filename = 'temp_ela.jpg'
            cv2.imwrite(temp_filename, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
            ela_img = cv2.imread(temp_filename)
            
            # Calculate difference
            if ela_img is not None:
                diff = cv2.absdiff(img, ela_img)
                diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                mean_diff = np.mean(diff_gray)
                
                if mean_diff > 5:
                    self.fraud_indicators.append({
                        "type": "Editing Traces",
                        "severity": "high",
                        "description": "Signs of image manipulation detected"
                    })
                    self.confidence_score -= 30
            
            # Check for copy-move forgery
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            sift = cv2.SIFT_create()
            kp, des = sift.detectAndCompute(gray, None)
            
            if des is not None and len(kp) > 50:
                bf = cv2.BFMatcher()
                matches = bf.knnMatch(des, des, k=2)
                
                suspicious_matches = 0
                for match_pair in matches:
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < 0.75 * n.distance:
                            suspicious_matches += 1
                
                if suspicious_matches > len(matches) * 0.3:
                    self.fraud_indicators.append({
                        "type": "Copy-Move Forgery",
                        "severity": "critical",
                        "description": "Possible copy-paste manipulation detected"
                    })
                    self.confidence_score -= 40
                    
        except Exception as e:
            logging.error(f"Error in editing trace detection: {e}")
    
    def check_upi_patterns(self, img):
        """Check for common UPI screenshot patterns"""
        try:
            height, width = img.shape[:2]
            
            # Expected regions in UPI screenshots
            top_region = img[0:int(height*0.2), 0:width]
            bottom_region = img[int(height*0.8):height, 0:width]
            
            # Check for header (usually has app logo)
            top_gray = cv2.cvtColor(top_region, cv2.COLOR_BGR2GRAY)
            top_variance = np.var(top_gray)
            
            if top_variance < 100:
                self.fraud_indicators.append({
                    "type": "Missing Header",
                    "severity": "medium",
                    "description": "Expected header region appears uniform"
                })
                self.confidence_score -= 15
            
            # Check for transaction amount prominence
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            white_pixels = np.sum(thresh == 255)
            
            if white_pixels < (height * width * 0.1):
                self.fraud_indicators.append({
                    "type": "Suspicious Brightness Pattern",
                    "severity": "medium",
                    "description": "Unusual brightness distribution"
                })
                self.confidence_score -= 10
                
        except Exception as e:
            logging.error(f"Error in UPI pattern check: {e}")
    
    def calculate_final_score(self):
        """Calculate final confidence score"""
        self.confidence_score = max(0, min(100, self.confidence_score))
    
    def generate_summary(self):
        """Generate human-readable summary"""
        if self.confidence_score >= 80:
            return "This appears to be a legitimate UPI transaction screenshot."
        elif self.confidence_score >= 60:
            return "Some suspicious elements detected. Please verify manually."
        elif self.confidence_score >= 40:
            return "Multiple fraud indicators detected. This is likely manipulated."
        else:
            return "High probability of fraud. Strong signs of tampering detected."
