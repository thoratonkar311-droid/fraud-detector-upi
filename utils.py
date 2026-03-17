import hashlib
from PIL import Image
import io
import logging

def check_image_metadata(image_bytes):
    """Check for suspicious metadata"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        metadata = img.info
        
        suspicious = []
        
        # Check for editing software traces
        editing_software = ['Photoshop', 'GIMP', 'Illustrator', 'Corel']
        for key, value in metadata.items():
            if any(software.lower() in str(value).lower() for software in editing_software):
                suspicious.append(f"Editing software detected: {value}")
        
        return suspicious
    except Exception as e:
        logging.error(f"Error checking metadata: {e}")
        return []

def detect_forgery_patterns(img_array):
    """Detect common forgery patterns"""
    try:
        import numpy as np
        from scipy import ndimage
        
        patterns = []
        
        # Check for inconsistencies in noise patterns
        noise = np.random.normal(0, 1, img_array.shape)
        noisy_img = img_array + noise * 10
        filtered = ndimage.median_filter(noisy_img, size=3)
        diff = np.abs(noisy_img - filtered)
        
        if np.mean(diff) > 20:
            patterns.append("Inconsistent noise pattern detected")
        
        return patterns
    except Exception as e:
        logging.error(f"Error detecting forgery patterns: {e}")
        return []
