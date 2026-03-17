from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from PIL import Image
import io
import logging
import os
from fraud_detector import UPIFraudDetector

app = Flask(__name__)

# Load configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
app.config['DEBUG'] = app.config['ENV'] == 'development'

# Configure CORS
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins)

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize detector with environment variables
detector = UPIFraudDetector(
    tesseract_path=os.environ.get('TESSERACT_PATH')
)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "environment": app.config['ENV']
    }), 200

@app.route('/detect', methods=['POST'])
def detect_fraud():
    """Main fraud detection endpoint"""
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({"error": "No image provided"}), 400
        
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Check file size
        image_bytes = base64.b64decode(image_data)
        if len(image_bytes) > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({
                "error": f"Image too large. Max size: {app.config['MAX_CONTENT_LENGTH']} bytes"
            }), 400
        
        # Decode and analyze image
        image = Image.open(io.BytesIO(image_bytes))
        result = detector.analyze(image)
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
