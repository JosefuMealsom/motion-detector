
import cv2
import numpy as np
from src.image_encoder import encode_image_for_web

class NormalAbsDiff:
    THRESH = 30
    ASSIGN_VALUE = 255
    ALPHA = 0.1

    MIN_AREA_ON_THRESHOLD = 8000
    MIN_AREA_OFF_THRESHOLD = 5000
    MIN_ZONE_FRAMES = 12

    is_background_set = False
    background = None
    cropped_image = None
    processed_image = None
    in_frame = False
    zone_config = {}
    time_in_zone = 0
    on_detect_callback = None

    def add_detect_callback(self, on_detect_callback):
        self.on_detect_callback = on_detect_callback

    def load_config(self, config):
        self.zone_config = config
        self.is_background_set = False

    def update_background(self, current_frame, alpha):
        bg = alpha * current_frame + (1 - alpha) * self.background
        bg = np.uint8(bg)  
        return bg
    
    def process(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # scale_percent = 25
        # width = int(frame.shape[1] * scale_percent/100)
        # height = int(frame.shape[0] * scale_percent/100)

        # frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

        if "zoneArea" in self.zone_config:
            tl = self.zone_config["zoneArea"]["topLeft"]
            br = self.zone_config["zoneArea"]["bottomRight"]
            frame = frame[tl["y"]:br["y"], tl["x"]:br["x"]]
            self.cropped_image = frame

        if "minDetectionArea" in self.zone_config:
            self.MIN_AREA_ON_THRESHOLD = self.zone_config["minDetectionArea"]
            self.MIN_AREA_OFF_THRESHOLD = self.MIN_AREA_ON_THRESHOLD * 0.8

        
        if self.is_background_set == False:
            self.background = frame
            self.is_background_set = True

            return False, None
        else:
            diff = cv2.absdiff(self.background, frame)
            ret, motion_mask = cv2.threshold(diff, self.THRESH, self.ASSIGN_VALUE, cv2.THRESH_BINARY)
            motion_mask = cv2.erode(motion_mask, None, iterations = 3)
            motion_mask = cv2.dilate(motion_mask, None, iterations = 5)
            motion_mask = cv2.GaussianBlur(motion_mask, (15,15), 0)
            ret, motion_mask = cv2.threshold(motion_mask, self.THRESH, self.ASSIGN_VALUE, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

            detections = []

            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                area = w*h
                # Reduce the area size needed for the user leaving the frame, prevent boundary errors
                activation_threshold = self.MIN_AREA_OFF_THRESHOLD if self.in_frame else self.MIN_AREA_ON_THRESHOLD
                if area > activation_threshold:
                    detections.append([x,y,x+w,y+h, area])

            for box in detections:
                cv2.rectangle(motion_mask, (box[0], box[1]), (box[2], box[3]), ( 255, 0, 0), 2 )
            
            if len(detections) > 0:
                self.time_in_zone = self.time_in_zone + 1
            else:
                self.time_in_zone = 0

            if not self.in_frame and self.time_in_zone > self.MIN_ZONE_FRAMES: 
                if self.on_detect_callback is not None:
                    self.on_detect_callback()
                self.in_frame = True
            elif len(detections) == 0 and self.in_frame:
                self.in_frame = False

            self.update_background(frame, 0.001)
            self.processed_image = motion_mask

    def reset_bg(self):
        self.bg_needs_update = True

    def cropped_jpeg(self):
        return encode_image_for_web(self.cropped_image)

    def bg_jpeg(self):
        return encode_image_for_web(self.background)
        
    def processed_jpeg(self):
        return encode_image_for_web(self.processed_image)
