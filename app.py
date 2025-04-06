from flask import Flask, Response, render_template
import cv2
import os
import time

app = Flask(__name__)

frame_rate = 30 # 30x slower playback
video_folder_path = "static/videos/"
video_file_name = "parking_video.mp4"
video_path = video_folder_path + video_file_name

@app.route('/')
def index():
    """Serve the index page"""
    return render_template('index.html')

def generate_video():
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

@app.route('/video_feed')
def video_feed():
    """Video streaming route for the detection app"""
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    host = '0.0.0.0' if os.environ.get('DOCKER') else '127.0.0.1'
    app.run(debug=True, host=host, port=port)
