import cv2
import numpy as np
from src.image_encoder import encode_image_for_web

class AdaptiveBGSubtractor:
    THRESH = 30
    ASSIGN_VALUE = 255
    ALPHA = 0.1

    MIN_AREA_ON_THRESHOLD = 8000
    MIN_AREA_OFF_THRESHOLD = 5000
    MIN_AREA_BG_UPDATE = None
    MAX_FRAMES_BG = 90

    is_background_set = False
    background = None
    cropped_image = None
    processed_image = None
    in_frame = False
    zone_config = {}
    bg_needs_update = False
    current_bg_update_frame = 0

    def load_config(self, config):
        self.zone_config = config
        self.is_background_set = False

    def update_background(self, current_frame, alpha):
        bg = alpha * current_frame + (1 - alpha) * self.background
        bg = np.uint8(bg)  
        return bg
    
    def process(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if "zoneArea" in self.zone_config:
            tl = self.zone_config["zoneArea"]["topLeft"]
            br = self.zone_config["zoneArea"]["bottomRight"]
            frame = frame[tl["y"]:br["y"], tl["x"]:br["x"]]
            self.cropped_image = frame

        if "minBgUpdateArea" in self.zone_config:
            self.MIN_AREA_BG_UPDATE = self.zone_config["minBgUpdateArea"]

        if "minDetectionArea" in self.zone_config:
            self.MIN_AREA_ON_THRESHOLD = self.zone_config["minDetectionArea"]
            self.MIN_AREA_OFF_THRESHOLD = self.MIN_AREA_ON_THRESHOLD * 0.8

        # Reset bg after timer
        if self.current_bg_update_frame == self.MAX_FRAMES_BG or self.bg_needs_update:
            self.background = frame
            self.current_bg_update_frame = 0
            self.bg_needs_update = False

        # scale_percent = 25
        # width = int(frame.shape[1] * scale_percent/100)
        # height = int(frame.shape[0] * scale_percent/100)

        # frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        
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

            update_bg = True
            update_bg_deferred = False
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                area = w*h
                # Reduce the area size needed for the user leaving the frame, prevent boundary errors
                activation_threshold = self.MIN_AREA_OFF_THRESHOLD if self.in_frame else self.MIN_AREA_ON_THRESHOLD
                if self.MIN_AREA_BG_UPDATE is not None and area > self.MIN_AREA_BG_UPDATE:
                    update_bg = False
                if self.MIN_AREA_BG_UPDATE is not None and area > self.MIN_AREA_BG_UPDATE * 1.5:
                    update_bg_deferred = True
                if area > activation_threshold:
                    detections.append([x,y,x+w,y+h, area])

            for box in detections:
                cv2.rectangle(motion_mask, (box[0], box[1]), (box[2], box[3]), ( 255, 0, 0), 2 )

            if len(detections) > 0 and not self.in_frame:
                self.in_frame = True
            elif len(detections) == 0 and self.in_frame:
                self.in_frame = False

            # Reset bg update if nothing being detected in zone after certain
            # number of frames
            if len(detections) == 0 and not update_bg and update_bg_deferred:
                self.current_bg_update_frame = self.current_bg_update_frame + 1

            # Only update the background if the user isn't in the frame, detects the presence
            # of the user in the zone.
            if update_bg:
                self.background = self.update_background(frame, alpha = self.ALPHA)

            self.processed_image = motion_mask

    def reset_bg(self):
        self.bg_needs_update = True

    def cropped_jpeg(self):
        return encode_image_for_web(self.cropped_image)

    def bg_jpeg(self):
        return encode_image_for_web(self.background)
        
    def processed_jpeg(self):
        return encode_image_for_web(self.processed_image)
