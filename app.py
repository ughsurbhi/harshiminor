import logging
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from waitress import serve

app = Flask(__name__)
CORS(app)

# Configuration
MODEL_PATH = "model.h5"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
SKIN_TONES = ["Type I", "Type II", "Type III", "Type IV", "Type V", "Type VI"]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Model loading failed: {str(e)}")
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(1, input_shape=(224, 224, 3))
    ])
    logger.warning("Using dummy model")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        prediction = model.predict(img_array)
        predicted_idx = int(np.argmax(prediction, axis=1)[0])
        
        return jsonify({
            "success": True,
            "prediction": predicted_idx,
            "confidence": float(np.max(prediction)),
            "skin_type": SKIN_TONES[predicted_idx]
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def run_server():
    port = int(os.environ.get('PORT', 5000))
    if os.environ.get('ENV') == 'PRODUCTION':
        serve(app, host="0.0.0.0", port=port, threads=4)
    else:
        app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == '__main__':
    run_server()
