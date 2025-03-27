import logging
import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_URL = "https://github.com/Hershy23/Color/releases/download/v2.0/model.h5"
MODEL_PATH = "model.h5"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Download model if not exists
if not os.path.exists(MODEL_PATH):
    logger.info("Downloading model...")
    try:
        response = requests.get(MODEL_URL)
        response.raise_for_status()
        with open(MODEL_PATH, "wb") as f:
            f.write(response.content)
        logger.info("Model downloaded successfully!")
    except Exception as e:
        logger.error(f"Failed to download model: {str(e)}")

# Load model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logger.info("Model loaded successfully!")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Check if file was uploaded
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({"error": "No file selected"}), 400
    
    # Check file type
    if not allowed_file(file.filename):
        logger.error("Invalid file type")
        return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG allowed"}), 400
    
    try:
        # Process image
        img = Image.open(file.stream).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        prediction = model.predict(img_array)
        predicted_label = int(np.argmax(prediction, axis=1)[0])
        
        logger.info(f"Prediction successful: {predicted_label}")
        return jsonify({
            "prediction": predicted_label,
            "confidence": float(np.max(prediction))
        })
    
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return jsonify({"error": "Prediction failed"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)