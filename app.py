from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from PIL import Image
import io
import logging
from fraud_detector import UPIFraudDetector

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

detector = UPIFraudDetector()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/detect', methods=['POST'])
def detect_fraud():
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({"error": "No image provided"}), 400
        
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Perform fraud detection
        result = detector.analyze(image)
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
