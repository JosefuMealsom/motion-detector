from src.video_stream import VideoStream
from src.adaptive_bg_subtraction import AdaptiveBGSubtractor
from flask import Flask, render_template, Response, request

app = Flask(__name__)
video_stream = VideoStream("rtsp://admin:P@ssw0rd@192.168.1.64:554/Streaming/channels/101")
zone_detector = AdaptiveBGSubtractor(video_stream)

@app.route("/stream/raw")
def stream_raw():
    return Response(generate_raw_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stream/processed")
def stream_processed():
    zone_detector.load_config()
    return Response(generate_processed_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

def generate_raw_frames():
    while True:
       success, image = video_stream.fetch_image()
       if success:
           yield image
           
def generate_processed_frames():
    while True:
       success, image = zone_detector.fetch_image()
       if success:
           yield image

@app.route("/zone", methods = ['POST'])
def save_zone():
    f = open("zone-position.json", "w")
    f.write(str(request.json).replace("'", "\""))
    f.close()
    zone_detector.load_config()
    return Response("SUCCESS")

if __name__ == "__main__":
    app.run(debug=True)

video_stream.release()
