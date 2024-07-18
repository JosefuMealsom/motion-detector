import cv2

def encode_image_for_web(frame):
    success, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    return (True, (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'))
