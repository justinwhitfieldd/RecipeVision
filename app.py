from flask import Flask, render_template, request, redirect, url_for, Response
from werkzeug.utils import secure_filename
import os
import cv2
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'photos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

camera = cv2.VideoCapture(0)  # 0 for default camera

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photo' not in request.files:
        return redirect(request.url)
    file = request.files['photo']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(filename)
        return 'Image uploaded and saved.'

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

@app.route('/capture', methods=['POST'])
def capture():
    success, frame = camera.read()  # Read the current frame from the video stream
    if success:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate a timestamp for the filename
        filename = f"{timestamp}.jpg"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(path, frame)  # Save the captured frame as a jpeg
        return f"Captured {filename}"
    else:
        return "Failed to capture photo", 500
    
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
