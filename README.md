# UPI Screenshot Fraud Detector

A real-time fraud detection system for UPI transaction screenshots using advanced image analysis and machine learning techniques.

## Features

- **Real-time Analysis**: Instant detection of fraudulent UPI screenshots
- **Multiple Detection Methods**:
  - Image quality and compression analysis
  - Screenshot artifact detection
  - Text consistency verification
  - Editing trace detection (ELA, copy-move forgery)
  - UPI pattern validation
- **Simple Interface**: Clean, user-friendly design
- **Confidence Scoring**: Detailed confidence metrics for each analysis
- **Fraud Indicators**: Clear listing of detected issues with severity levels

## Technology Stack

- **Backend**: Python Flask with OpenCV, PIL, Tesseract OCR
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Ready for Render/GitHub Pages

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/upi-fraud-detector.git
cd upi-fraud-detector
