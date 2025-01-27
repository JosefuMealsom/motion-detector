from src.video_stream import VideoStream
from src.normal_abs_diff import NormalAbsDiff
from flask import Flask, render_template, Response, request
from threading import Thread, active_count
from src.config_loader import load_config, save_config
from flask_socketio import SocketIO
import argparse
from src.udp_socket import UdpSocket
from src.mjpeg_stream import fetch_mjpeg_stream 

parser = argparse.ArgumentParser("IR motion detector")
parser.add_argument("--udp-host", help="The host to send messages to", required=True)
parser.add_argument("--udp-port", help="The port to send messages to", type=int, required=True)
parser.add_argument("--stream-url", "-surl", help="The url of the stream", required=True)
parser.add_argument("--stream-user", "-suser", help="The user to log into the stream", required=True)
parser.add_argument("--stream-password", "-spass", help="The password to log into the stream", required=True)

args = parser.parse_args()
host = args.udp_host
port = args.udp_port
stream_url = args.stream_url
stream_user = args.stream_user
stream_password = args.stream_password

udp_socket = UdpSocket(host, port)

app = Flask(__name__)
socketio = SocketIO(app)
    
def on_detect(entered):
    if entered:
        udp_socket.send_message("zone:entered")
        socketio.emit("entered")
    else:
        udp_socket.send_message("zone:left")
        socketio.emit("left")


zone_detector = NormalAbsDiff()

result, config = load_config()
if result:
    zone_detector.load_config(config)

zone_detector.add_detect_callback(on_detect)

mjpeg_stream_generator = fetch_mjpeg_stream(stream_url, stream_user, stream_password)

def process_stream():
    while True:
        frame = next(mjpeg_stream_generator)
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

@app.route("/stream/raw-difference")
def stream_raw_difference():
    return Response(
        generate_raw_difference_frames(),
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
        success, image = zone_detector.raw_stream()
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

def generate_raw_difference_frames():
    while True:
        success, image = zone_detector.raw_difference_jpeg()
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
    socketio.run(app, debug=False)
