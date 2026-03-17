class UPIFraudDetector {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.apiUrl = process.env.NODE_ENV === 'production' 
            ? 'https://your-backend-url.onrender.com' 
            : 'http://localhost:5000';
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.previewContainer = document.getElementById('previewContainer');
        this.preview = document.getElementById('preview');
        this.changeBtn = document.getElementById('changeBtn');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.resultsSection = document.getElementById('resultsSection');
        this.fraudIndicators = document.getElementById('fraudIndicators');
        this.summaryText = document.getElementById('summaryText');
        this.verdict = document.getElementById('verdict');
        this.confidenceFill = document.getElementById('confidenceFill');
        this.confidenceValue = document.getElementById('confidenceValue');
    }

    attachEventListeners() {
        // Upload area click
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                this.handleFile(file);
            }
        });

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFile(file);
            }
        });

        // Change button
        this.changeBtn.addEventListener('click', () => {
            this.resetUpload();
        });

        // Analyze button
        this.analyzeBtn.addEventListener('click', () => {
            this.analyzeImage();
        });
    }

    handleFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.preview.src = e.target.result;
            this.uploadArea.style.display = 'none';
            this.previewContainer.style.display = 'block';
            this.analyzeBtn.disabled = false;
            this.currentImage = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    resetUpload() {
        this.uploadArea.style.display = 'block';
        this.previewContainer.style.display = 'none';
        this.analyzeBtn.disabled = true;
        this.resultsSection.style.display = 'none';
        this.fileInput.value = '';
        this.currentImage = null;
    }

    async analyzeImage() {
        if (!this.currentImage) return;

        // Show loading state
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.querySelector('.btn-text').style.display = 'none';
        this.analyzeBtn.querySelector('.btn-loader').style.display = 'inline-block';

        try {
            const response = await fetch(`${this.apiUrl}/detect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: this.currentImage
                })
            });

            const data = await response.json();
            this.displayResults(data);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while analyzing the image. Please try again.');
        } finally {
            // Hide loading state
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.querySelector('.btn-text').style.display = 'inline';
            this.analyzeBtn.querySelector('.btn-loader').style.display = 'none';
        }
    }

    displayResults(data) {
        this.resultsSection.style.display = 'block';
        
        // Update confidence meter
        this.confidenceFill.style.width = `${data.confidence_score}%`;
        this.confidenceValue.textContent = `${Math.round(data.confidence_score)}%`;
        
        // Update fraud indicators
        this.fraudIndicators.innerHTML = '';
        if (data.fraud_indicators && data.fraud_indicators.length > 0) {
            data.fraud_indicators.forEach(indicator => {
                const card = this.createIndicatorCard(indicator);
                this.fraudIndicators.appendChild(card);
            });
        } else {
            this.fraudIndicators.innerHTML = '<p class="no-indicators">No fraud indicators detected</p>';
        }
        
        // Update summary
        this.summaryText.textContent = data.analysis_summary;
        
        // Update verdict
        this.verdict.className = 'verdict';
        if (data.is_fraudulent) {
            this.verdict.classList.add('fraud');
            this.verdict.textContent = '⚠️ FRAUD DETECTED - This screenshot shows signs of tampering';
        } else if (data.confidence_score < 80) {
            this.verdict.classList.add('warning');
            this.verdict.textContent = '⚠️ SUSPICIOUS - Manual verification recommended';
        } else {
            this.verdict.classList.add('safe');
            this.verdict.textContent = '✅ SAFE - No signs of tampering detected';
        }
    }

    createIndicatorCard(indicator) {
        const card = document.createElement('div');
        card.className = `indicator-card ${indicator.severity}`;
        
        card.innerHTML = `
            <div class="indicator-header">
                <span class="indicator-title">${indicator.type}</span>
                <span class="indicator-severity severity-${indicator.severity}">${indicator.severity.toUpperCase()}</span>
            </div>
            <p class="indicator-description">${indicator.description}</p>
        `;
        
        return card;
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    new UPIFraudDetector();
});
