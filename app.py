from flask import Flask, Response, render_template
import cv2
import os
import time
import threading
import queue

app = Flask(__name__)

# Configuration
VIDEO_FOLDER_PATH = "static/videos/"
VIDEO_FILE_NAME = "parking_video.mp4"
VIDEO_PATH = os.path.join(VIDEO_FOLDER_PATH, VIDEO_FILE_NAME)
SLOWDOWN_FACTOR = 30  # Playback 30x slower than real-time
FRAME_QUEUE = queue.Queue(maxsize=10)  # Buffer for frames
RUNNING = True  # Control background thread

def background_video_reader():
    """Read video in the background and push frames to a queue."""
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error: Could not open video {VIDEO_PATH}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = (1 / fps) * SLOWDOWN_FACTOR  # Delay for slower playback

    while RUNNING:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            continue

        # Encode frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            frame_data = jpeg.tobytes()
            # Put frame in queue (drop old frames if queue is full)
            try:
                FRAME_QUEUE.put_nowait(frame_data)
            except queue.Full:
                pass

        time.sleep(frame_delay)

    cap.release()

@app.route('/')
def index():
    """Serve the index page."""
    return render_template('index.html')

def generate_video():
    """Stream frames from the queue to clients."""
    while True:
        try:
            # Get the latest frame from the queue
            frame_data = FRAME_QUEUE.get(timeout=1)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n\r\n')
        except queue.Empty:
            continue  # Keep trying if queue is empty momentarily

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Ensure video file exists
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Video file {VIDEO_PATH} not found")
        exit(1)

    # Start background thread
    threading.Thread(target=background_video_reader, daemon=True).start()

    # Run Flask app
    port = int(os.environ.get("PORT", 5001))
    host = '0.0.0.0' if os.environ.get('DOCKER') else '127.0.0.1'
    app.run(debug=True, host=host, port=port, use_reloader=False)