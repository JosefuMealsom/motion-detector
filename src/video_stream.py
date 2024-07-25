import cv2
import src.freshest_frame as freshest_frame
from src.image_encoder import encode_image_for_web

class VideoStream:
    def __init__(self, rtsp_url):
        self.stream = freshest_frame.FreshestFrame(cv2.VideoCapture(rtsp_url))
        #self.stream = cv2.VideoCapture(rtsp_url)
        self.current_frame = None

    def read_next_frame(self):
        success, frame = self.stream.read()
        if success:
            self.current_frame = frame
            return success, frame
        else:
            self.stream.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return False, None

    def jpeg(self):
        return encode_image_for_web(self.current_frame)

    def release(self):
        self.stream.release()
