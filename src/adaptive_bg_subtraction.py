import cv2
import numpy as np
from src.image_encoder import encode_image_for_web
import json

THRESH = 20
ASSIGN_VALUE = 255
ALPHA = 0.1

MIN_AREA_ON_THRESHOLD = 8000
MIN_AREA_OFF_THRESHOLD = 5000
MIN_AREA_BG_UPDATE = 200


class AdaptiveBGSubtractor:
    def __init__(self):
        self.is_background_set = False
        self.background = None
        self.cropped_image = None
        self.processed_image = None
        self.in_frame = False
        self.zone_config = None

    def load_config(self):
        try:
            f = open("zone.json", "r")
            self.zone_config = json.loads(f.read())
            f.close()
            self.is_background_set = False
        except:
            print("Zone file not found") 


    def update_background(self, current_frame, alpha):
        bg = alpha * current_frame + (1 - alpha) * self.background
        bg = np.uint8(bg)  
        return bg
    
    def process(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.zone_config is not None:
            tl = self.zone_config["zoneArea"]["topLeft"]
            br = self.zone_config["zoneArea"]["bottomRight"]
            frame = frame[tl["y"]:br["y"], tl["x"]:br["x"]]
            MIN_AREA_ON_THRESHOLD = self.zone_config["minArea"]
            MIN_AREA_OFF_THRESHOLD = MIN_AREA_ON_THRESHOLD * 0.8
            self.cropped_image = frame

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
            ret, motion_mask = cv2.threshold(diff, THRESH, ASSIGN_VALUE, cv2.THRESH_BINARY)
            motion_mask = cv2.erode(motion_mask, None, iterations = 2)
            motion_mask = cv2.dilate(motion_mask, None, iterations = 5)
            motion_mask = cv2.GaussianBlur(motion_mask, (15,15), 0)
            ret, motion_mask = cv2.threshold(motion_mask, THRESH, ASSIGN_VALUE, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

            detections = []

            update_bg = True
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                area = w*h
                # Reduce the area size needed for the user leaving the frame, prevent boundary errors
                activation_threshold = MIN_AREA_OFF_THRESHOLD if self.in_frame else MIN_AREA_ON_THRESHOLD
                #if area > MIN_AREA_BG_UPDATE:
                #    update_bg = False
                if area > activation_threshold:
                    detections.append([x,y,x+w,y+h, area])

            for box in detections:
                cv2.rectangle(motion_mask, (box[0], box[1]), (box[2], box[3]), ( 255, 0, 0), 2 )

            if len(detections) > 0 and not self.in_frame:
                self.in_frame = True
            elif len(detections) == 0 and self.in_frame:
                self.in_frame = False

            # Only update the background if the user isn't in the frame, detects the presence
            # of the user in the zone.
            if not self.in_frame:
                self.background = self.update_background(frame, alpha = ALPHA)

            self.processed_image = motion_mask

    def cropped_jpeg(self):
        return encode_image_for_web(self.cropped_image)

    def processed_jpeg(self):
        return encode_image_for_web(self.processed_image)
