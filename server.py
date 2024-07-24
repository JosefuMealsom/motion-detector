from src.video_stream import VideoStream
from src.adaptive_bg_subtraction import AdaptiveBGSubtractor
from src.normal_abs_diff import NormalAbsDiff
from flask import Flask, render_template, Response, request
from threading import Thread
from src.config_loader import load_config, save_config
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
#video_stream = VideoStream("rtsp://admin:P@ssw0rd@192.168.1.64:554/Streaming/channels/101")
video_stream = VideoStream("test-output.mp4")
    
def on_detect(entered):
    if entered:
        socketio.emit("entered")
    else:
        socketio.emit("left")


zone_detector = NormalAbsDiff()

result, config = load_config()
if result:
    zone_detector.load_config(config)

zone_detector.add_detect_callback(on_detect)


def process_stream():
    while True:
        success, frame = video_stream.read_next_frame()
        if not success:
            continue
        zone_detector.process(frame)


process_thread = Thread(target=process_stream)
process_thread.start()


@app.route("/stream/raw")
def stream_raw():
    return Response(
        generate_raw_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/stream/cropped")
def stream_cropped():
    return Response(
        generate_cropped_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/stream/processed")
def stream_processed():
    return Response(
        generate_processed_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/stream/background")
def stream_background():
    return Response(
        generate_bg_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/")
def index():
    return render_template("index.html")


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


def generate_bg_frames():
    while True:
        success, image = zone_detector.bg_jpeg()
        if success:
            yield image


@app.route("/zone", methods=["POST"])
def save_zone():
    # Need proper validation here, not important atm
    save_config(request.json)
    zone_detector.load_config(request.json)
    return {"status": "success"}, 200


@app.route("/zone/reset", methods=["POST"])
def reset_zone():
    zone_detector.reset_bg()
    return {"status": "success"}, 200


if __name__ == "__main__":
    socketio.run(app, debug=True)

video_stream.release()
