import cv2
import numpy as np
import freshest_frame
import time

MAX_FRAMES = 1000
LEARNING_RATE = -1   
THRESH = 50
ASSIGN_VALUE = 255

fgbg = cv2.createBackgroundSubtractorKNN()

time.sleep(5)

cap = cv2.VideoCapture("rtsp://admin:P@ssw0rd@192.168.1.64:554/Streaming/channels/101")
cap = freshest_frame.FreshestFrame(cap)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    scale_percent = 25
    width = int(frame.shape[1] * scale_percent/100)
    height = int(frame.shape[0] * scale_percent/100)
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    frame = cv2.erode(frame, None, iterations = 2)
    frame = cv2.dilate(frame, None, iterations = 5)
    frame = cv2.GaussianBlur(frame, (15,15), 0)
    ret, frame = cv2.threshold(frame, THRESH, ASSIGN_VALUE, cv2.THRESH_BINARY)

    #Apply MOG 
    motion_mask = fgbg.apply(frame, LEARNING_RATE)
    #Get background
    background = fgbg.getBackgroundImage()
    # Display the motion mask and background
    cv2.imshow('background', background)
    cv2.imshow('Motion Mask', motion_mask) 
    key = cv2.waitKey(1)
    if key == 27:
        break
    
cap.release()
