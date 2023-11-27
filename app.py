from flask import Flask, render_template,session, request, redirect, url_for, Response, make_response,jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from recipeGeneration import recipes_bp, get_recipes
from imageGrabba import fetch_image_url
from flask import Flask, render_template, session, request, redirect, url_for, Response, send_from_directory
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import tempfile
import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
from models.experimental import attempt_load
from utils.datasets import LoadImages
from utils.general import non_max_suppression

def create_app():

    app = Flask(__name__)
    # Error 404 handler
    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error=str(e)), 404
    # Error 405 handler
    @app.errorhandler(405)
    def resource_not_found(e):
        return jsonify(error=str(e)), 405
    # Error 401 handler
    @app.errorhandler(401)
    def custom_401(error):
        return Response("API Key required.", 401)
    @app.route("/ping")
    def hello_world():
        return "pong"
  
    return app
  
app = create_app()
app.register_blueprint(recipes_bp)
app.secret_key = 'secret'

UPLOAD_FOLDER = 'photos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# camera = cv2.VideoCapture(0)  # 0 for default camera
# Initialize YOLOv7 model
model = attempt_load('best.pt')  # Load the YOLOv7 model
class_names = model.module.names if hasattr(model, 'module') else model.names

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device).eval()
print("Model loaded successfully!")

recognized_ingredients = []
@app.route('/')
def landing():
    return render_template('landingPage.html')
def resize_image(image, divisor=32):
    h, w = image.shape[:2]
    h = h - (h % divisor)
    w = w - (w % divisor)
    return cv2.resize(image, (w, h))

def run_inference(image_path):
    # Perform inference and return detected items (ingredients in this case)
    detected_ingredients = []
    
    # Run inference
    img_cv2 = cv2.imread(image_path)
    img_cv2 = resize_image(img_cv2)  # Resize the image if necessary
    img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)  # Convert color from BGR to RGB

    # Transpose the image dimensions and normalize pixel values
    img_cv2 = img_cv2.transpose(2, 0, 1)
    img_cv2 = img_cv2 / 255.0

    # Convert image to a PyTorch tensor and add a batch dimension
    img = torch.from_numpy(img_cv2).float().unsqueeze(0).to(device)
    print(f"Input dimensions: {img.shape}")

    # Run the model and get predictions
    print("Running inference...")
    pred = model(img)[0]  # Get predictions from the model
    print(f"Raw predictions: {pred}")

    # Ensure 'pred' is a tensor before calling non_max_suppression
    if not isinstance(pred, torch.Tensor):
        print("Pred is not a tensor. Non-max suppression cannot be applied.")
        return detected_ingredients

    # Apply Non-Max Suppression to filter predictions
    pred = non_max_suppression(pred, 0.35, 0.45)
    print(f"After non_max_suppression: {pred}")  # Debug print

    # Process detections
    for det in pred:
        if det is not None and len(det):
            # Iterate over each detection in the image
            for *xyxy, conf, cls in reversed(det):
                class_idx = int(cls.item())  # Get class index
                class_name = class_names[class_idx]  # Get class name from the model's class names
                detected_ingredients.append(class_name)  # Append detected ingredient

    return detected_ingredients

@app.route('/camera')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global recognized_ingredients
    print("Received file upload request.")
    file = request.files.get('photo')  # Use .get to avoid KeyError

    if file:
        print("File received. Starting processing.")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate a timestamp for the filename
        filename = f"{timestamp}.jpg"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        # Run YOLOv7 inference here and update recognized_ingredients
        recognized_ingredients = run_inference(path)
        print(f"Processing completed. Recognized Ingredients: {recognized_ingredients}")

        return redirect(url_for('ingredients'))
    else:
        return "No file uploaded", 400  # Bad request

def generate_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


from flask import jsonify

@app.route('/capture', methods=['POST'])
def capture():
    global recognized_ingredients
    file = request.files.get('photo')
    
    if file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.jpg"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        recognized_ingredients = run_inference(path)
        return jsonify({"status": "success", "filePath": filename})
    else:
        return jsonify({"status": "failure"}), 400

@app.route('/upload_captured', methods=['POST'])
def upload_captured():
    global recognized_ingredients
    file_path = request.form.get('capturedFilePath')
    
    if file_path:
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        
        recognized_ingredients = run_inference(full_path)
        return redirect(url_for('ingredients'))
    else:
        return "No captured file", 400

    
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/ingredients')
def ingredients():
    return render_template('ingredients.html', ingredients=recognized_ingredients)
@app.route('/recipes')
def recipes_page():
    recipes = session.get('recipes', [])  # Get recipes from session
    for recipe in recipes:
        recipe_name = recipe['name']
        recipe['image_url'] = fetch_image_url(recipe_name)
    return render_template('recipes.html', recipes=recipes)
# TODO if null dont resubmit it

@app.route('/get_recognized_ingredients', methods=['GET'])
def get_recognized_ingredients():
    global recognized_ingredients
    return jsonify({"recognized_ingredients": recognized_ingredients})


if __name__ == '__main__':
    print(" Starting app...")
    app.run(host="0.0.0.0", port=5000)
