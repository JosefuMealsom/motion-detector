import cv2
import requests
import numpy as np
from requests.auth import HTTPDigestAuth


def fetch_mjpeg_stream(url, user, password):
    data = b'' 
    r = requests.get(url, auth=HTTPDigestAuth(user, password), stream=True)
    if(r.status_code == 200):
        for chunk in r.iter_content(chunk_size=1024):
            data += chunk
            a = data.find(b'\xff\xd8')
            b = data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = data[a:b+2]
                data = data[b+2:]
                yield cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
    else:
        print("Received unexpected status code {}".format(r.status_code))
