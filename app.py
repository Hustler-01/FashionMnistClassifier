from flask import Flask, request, render_template, jsonify
import numpy as np
import pickle
import cv2

app = Flask(__name__)

# --- Load trained SVM model ---
with open("svm_model.pkl", "rb") as f:
    model = pickle.load(f)

# Fashion MNIST class labels
class_names = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"
]

# --- Preprocess custom image like Fashion MNIST ---
def preprocess_image(img_bytes):
    # Convert to grayscale
    file_bytes = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    # Invert (white bg → black bg like MNIST)
    img = cv2.bitwise_not(img)

    # Resize to 28x28
    img_resized = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)

    # Normalize and flatten
    img_resized = img_resized.astype("float32") / 255.0
    img_flat = img_resized.reshape(1, -1)

    return img_flat

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    img_flat = preprocess_image(file.read())

    # Predict using SVM
    pred = model.predict(img_flat)[0]
    label = class_names[pred]

    return jsonify({"class_id": int(pred), "label": label})

if __name__ == '__main__':
    app.run(debug=True)