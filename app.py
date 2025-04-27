from flask import Flask, Response, render_template
import cv2
import os
import time
import urllib.parse

app = Flask(__name__)

frame_rate = 30 # 30x slower playback
video_folder_path = "static/videos/"
video_file_name = "parking_video.mp4"
video_path = video_folder_path + video_file_name

CAMERA_SOURCES = {
    'PLV-0001': 0,
    'PLV-0002': 1,
    'PLV-0003': 2
}

parking_camera_sources = [
    { 'id': 'PLV-0001', 'title': 'Front Gate', 'identifier': 'PLV-0001', 'address': '123 Main St' },
    { 'id': 'PLV-0002', 'title': 'Back Entrance', 'identifier': 'PLV-0002', 'address': '456 Oak Ave' },
    { 'id': 'PLV-0003', 'title': 'Parking Lot', 'identifier': 'PLV-0003', 'address': '789 Pine Rd' }
]

# Custom Jinja filter for URL encoding
@app.template_filter('url_encode')
def url_encode_filter(s):
    return urllib.parse.quote_plus(s)

@app.route('/')
def index():
    """Serve the index page"""
    return render_template('index.html', parking_camera_sources=parking_camera_sources)

def generate_video(camera_id):
    # source = CAMERA_SOURCES.get(camera_id)
    # if source is None:
    #     # If invalid ID, return a single blank frame or an error image
    #     return
    
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1 / (frame_rate / frame_rate)

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            continue

        # Encode the frame in JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        # Convert to byte data
        frame_data = jpeg.tobytes()

        # Yield the frame as an HTTP response with the correct MIME type
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n\r\n')

        # Wait before sending the next frame (simulate slow playback)
        time.sleep(frame_delay)

    cap.release()

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    """Video streaming route for the detection app"""
    return Response(
        generate_video(camera_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    host = '0.0.0.0' if os.environ.get('DOCKER') else '127.0.0.1'
    app.run(debug=True, host=host, port=port)
