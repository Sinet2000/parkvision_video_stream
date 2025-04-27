from flask import Flask, Response, render_template
import cv2
import os
import time
import urllib.parse
import threading
import queue

app = Flask(__name__)

# Configuration
default_folder = os.path.join(os.path.dirname(__file__), 'static', 'videos')
VIDEO_FOLDER_PATH = default_folder

parking_camera_sources = [
    { 'id': 'PLV-0001', 'title': 'Front Gate', 'identifier': 'PLV-0001', 'address': 'Krišjāņa Barona iela 1, Rīga, LV-1050', 'latitude': 56.9547093, 'longitude': 24.1560588 },
    { 'id': 'PLV-0002', 'title': 'Back Entrance', 'identifier': 'PLV-0002', 'address': 'Elizabetes iela 2, Rīga, LV-1010', 'latitude': 56.9474850, 'longitude': 24.1115221 },
    { 'id': 'PLV-0003', 'title': 'Parking Lot', 'identifier': 'PLV-0003', 'address': 'Miķeļa iela, Rīga, LV-1010', 'latitude': 56.95571405810339, 'longitude': 24.099527971722647 },
    { 'id': 'PLV-0004', 'title': 'Parking Lot', 'identifier': 'PLV-0003', 'address': 'Republikas Laukums 2A, Rīga, LV-1010', 'latitude': 56.9535827, 'longitude': 24.100376016713284 }
]

def generate_video(camera_id):
    """
    Stream video file for given camera_id with slowdown.
    File name derived as parkingXXXX_video.mp4 from ID.
    """
    # Extract numeric part: PLV-0001 -> 0001
    suffix = camera_id.split('-')[-1]
    filename = f"parking{suffix}_video.mp4"
    path = os.path.join(VIDEO_FOLDER_PATH, filename)

    if not os.path.exists(path):
        # If file missing, stop generator
        return

    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    slowdown = 8
    delay = (1.0 / fps) * slowdown

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(delay)

    cap.release()

# Custom Jinja filter for URL encoding
@app.template_filter('url_encode')
def url_encode_filter(s):
    return urllib.parse.quote_plus(s)

@app.route('/')
def index():
    """Serve the index page"""
    return render_template('index.html', parking_camera_sources=parking_camera_sources)

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    return Response(
        generate_video(camera_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    # Ensure video folder exists
    if not os.path.isdir(VIDEO_FOLDER_PATH):
        print(f"Error: Video folder {VIDEO_FOLDER_PATH} not found.")
        exit(1)

    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    app.run(host=host, port=port, threaded=True, debug=False)