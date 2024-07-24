import cv2
import numpy as np
from src.image_encoder import encode_image_for_web

class NormalAbsDiff:
    THRESH = 30
    ASSIGN_VALUE = 255
    ALPHA = 0.1

    MIN_AREA_ON_THRESHOLD = 8000
    MIN_AREA_OFF_THRESHOLD = 5000
    MIN_ZONE_FRAMES = 30
    IMAGE_SCALE = 100

    is_background_set = False
    background = None
    background_needs_update = False
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

        if "threshold" in self.zone_config:
             self.THRESH = self.zone_config["threshold"]

        if "scale" in self.zone_config:
            self.IMAGE_SCALE = self.zone_config["scale"]
            
        if "minDetectionArea" in self.zone_config:
            self.MIN_AREA_ON_THRESHOLD = self.zone_config["minDetectionArea"] * self.IMAGE_SCALE / 100
            self.MIN_AREA_OFF_THRESHOLD = self.MIN_AREA_ON_THRESHOLD * 0.8 * self.IMAGE_SCALE / 100

        if "minTime" in self.zone_config:
            self.MIN_ZONE_FRAMES = self.zone_config["minTime"]

    def update_background(self, current_frame, alpha):
        bg = alpha * current_frame + (1 - alpha) * self.background
        bg = np.uint8(bg)
        return bg

    def process(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if "zoneArea" in self.zone_config:
            tl = self.zone_config["zoneArea"]["topLeft"]
            br = self.zone_config["zoneArea"]["bottomRight"]
            frame = frame[tl["y"] : br["y"], tl["x"] : br["x"]]

            if self.IMAGE_SCALE < 100:
                height, width = frame.shape
                width = int(width * self.IMAGE_SCALE /100)
                height = int(height * self.IMAGE_SCALE/100)
                frame = cv2.resize(frame, (width, height), )

            self.cropped_image = frame

        if self.background_needs_update:
            self.background = frame
            self.background_needs_update = False

        if self.is_background_set == False:
            self.background = frame
            self.is_background_set = True

            return False, None
        else:
            diff = cv2.absdiff(self.background, frame)
            ret, motion_mask = cv2.threshold(
                diff, self.THRESH, self.ASSIGN_VALUE, cv2.THRESH_BINARY
            )
            motion_mask = cv2.erode(motion_mask, None, iterations=3)
            motion_mask = cv2.dilate(motion_mask, None, iterations=5)
            motion_mask = cv2.GaussianBlur(motion_mask, (15, 15), 0)
            ret, motion_mask = cv2.threshold(
                motion_mask, self.THRESH, self.ASSIGN_VALUE, cv2.THRESH_BINARY
            )
            contours, _ = cv2.findContours(
                motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1
            )

            detections = []

            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                area = w * h
                # Reduce the area size needed for the user leaving the frame, prevent boundary errors
                activation_threshold = (
                    self.MIN_AREA_OFF_THRESHOLD
                    if self.in_frame
                    else self.MIN_AREA_ON_THRESHOLD
                )
                if area > activation_threshold:
                    detections.append([x, y, x + w, y + h, area])

            for box in detections:
                cv2.rectangle(
                    motion_mask, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 2
                )

            if len(detections) > 0:
                self.time_in_zone = self.time_in_zone + 1
            else:
                self.time_in_zone = 0

            if not self.in_frame and self.time_in_zone > self.MIN_ZONE_FRAMES:
                if self.on_detect_callback is not None:
                    self.on_detect_callback(True)
                self.in_frame = True
            elif len(detections) == 0 and self.in_frame:
                self.in_frame = False
                self.on_detect_callback(False)

            self.update_background(frame, 0.05)
            self.processed_image = motion_mask

    def reset_bg(self):
        self.background_needs_update = True

    def cropped_jpeg(self):
        return encode_image_for_web(self.cropped_image)

    def bg_jpeg(self):
        return encode_image_for_web(self.background)

    def processed_jpeg(self):
        return encode_image_for_web(self.processed_image)
