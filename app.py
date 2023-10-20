from flask import Flask, render_template,session, request, redirect, url_for, Response, make_response
from werkzeug.utils import secure_filename
import os
import cv2
from datetime import datetime
from recipeGeneration import recipes_bp, get_recipes
from imageGrabba import fetch_image_url
import sys
from flask import Flask, render_template, session, request, redirect, url_for, Response
import os
import cv2
from datetime import datetime
import torch
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageGrab, Image, ImageTk
import cv2
import threading
import argparse
import time
from pathlib import Path
import tempfile
import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
import os
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import threading
from models.experimental import attempt_load
from utils.datasets import LoadImages
from utils.general import non_max_suppression
app = Flask(__name__)
app.register_blueprint(recipes_bp)
app.secret_key = 'secret'
class_names = ['-', 'almond', 'apple', 'avocado', 'beef', 'bell pepper', 'blueberry', 'bread', 'broccoli', 'butter', 'carrot', 'cheese', 'chilli', 'cookie', 'corn', 'cucumber', 'egg', 'eggplant', 'garlic', 'lemon', 'milk', 'mozarella cheese', 'mushroom', 'mussel', 'onion', 'oyster', 'parmesan cheese', 'pasta', 'pork rib', 'potato', 'salmon', 'scallop', 'shrimp', 'strawberry', 'toast bread', 'tomato', 'tuna', 'yogurt']

UPLOAD_FOLDER = 'photos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# camera = cv2.VideoCapture(0)  # 0 for default camera
# Initialize YOLOv7 model
model = attempt_load('best.pt')  # Load the YOLOv7 model
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
    img_cv2 = resize_image(img_cv2)
    img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)

    img_cv2 = img_cv2.transpose(2, 0, 1)
    img_cv2 = img_cv2 / 255.0
    img = torch.from_numpy(img_cv2).float().unsqueeze(0).to(device)
    print(f"Input dimensions: {img.shape}")
    print("Running inference...")
    pred = model(img)[0]
    print(f"Raw predictions: {pred}")

    pred = non_max_suppression(pred, 0.35, 0.45)
    print(f"After non_max_suppression: {pred}")  # Debug print

    for det in pred:
        if det is not None and len(det):
            for *xyxy, conf, cls in reversed(det):
                print(f"Confidence: {conf}, Class: {cls}")  # Debug print
                # Convert tensor to Python number and get the corresponding class name
                class_idx = int(cls.item())
                class_name = class_names[class_idx]
                detected_ingredients.append(class_name)
        else:
            print("No detections passed the non_max_suppression.")  # Debug print

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
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)), ssl_context = "adhoc")

