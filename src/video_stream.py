import cv2
import src.freshest_frame as freshest_frame
from src.image_encoder import encode_image_for_web

class VideoStream:
    def __init__(self, rtsp_url):
        self.stream = freshest_frame.FreshestFrame(cv2.VideoCapture(rtsp_url))

    def fetch_image(self):
        success, frame = self.stream.read()
        if not success:
            return (False, None) 
        else:
            return encode_image_for_web(frame)

    def release(self):
        self.stream.release()
