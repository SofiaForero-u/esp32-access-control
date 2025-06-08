from flask import Flask, request
import cv2
import numpy as np

app = Flask(__name__)

img_autorizada = cv2.imread("rostro_autorizado.jpg", 0)
orb = cv2.ORB_create()
kp1, des1 = orb.detectAndCompute(img_autorizada, None)

@app.route('/verificar', methods=['GET'])
def verificar():
    return "Esperando imagen..."

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']
    img_np = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(img_np, cv2.IMREAD_GRAYSCALE)

    kp2, des2 = orb.detectAndCompute(frame, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    if des2 is None:
        return "FAIL"

    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    if len(matches) > 10:
        return "OK"
    else:
        return "FAIL"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
