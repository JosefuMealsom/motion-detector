from src.video_stream import VideoStream
from src.adaptive_bg_subtraction import AdaptiveBGSubtractor
from flask import Flask, render_template, Response, request
from threading import Thread
import json

app = Flask(__name__)
video_stream = VideoStream("rtsp://admin:P@ssw0rd@192.168.1.64:554/Streaming/channels/101")
zone_detector = AdaptiveBGSubtractor()

def process_stream():
    zone_detector.load_config()
    while True:
        success, frame = video_stream.read_next_frame()
        if not success: continue
        zone_detector.process(frame)

process_thread = Thread(target=process_stream)
process_thread.start()

@app.route("/stream/raw")
def stream_raw():
    return Response(generate_raw_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stream/cropped")
def stream_cropped():
    return Response(generate_cropped_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stream/processed")
def stream_processed():
    zone_detector.load_config()
    return Response(generate_processed_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

def generate_raw_frames():
    while True:
       success, image = video_stream.jpeg()
       if success:
           yield image
           
def generate_cropped_frames():
    while True:
       success, image = zone_detector.cropped_jpeg()
       if success:
           yield image

def generate_processed_frames():
    while True:
       success, image = zone_detector.processed_jpeg()
       if success:
           yield image

@app.route("/zone", methods = ['POST'])
def save_zone():
    f = open("zone.json", "w+")
    zone_config = json.loads(f.read())
    zone_config["zoneArea"] = str(request.json);  
    f.write(str(request.json).replace("'", "\""))
    f.close()
    zone_detector.load_config()
    return Response("SUCCESS")

@app.route("/zone/min-area", methods = ['POST'])
def save_min_area():
    f = open("zone.json", "w+")
    zone_config = json.loads(f.read())
    zone_config["minArea"] = str(request.json);  
    f.write(str(request.json).replace("'", "\""))
    f.close()
    zone_detector.load_config()
    return Response("SUCCESS")

if __name__ == "__main__":
    app.run(debug=True)

video_stream.release()
