# -*- coding: utf-8 -*-
from flask import Blueprint, Response, request, jsonify
from naoqi import ALProxy
from pepper.connection import get_session
from PIL import Image
import numpy as np
import io
import time
import cv2
import tempfile
import requests

camera_routes = Blueprint('camera', __name__)

# MJPEG Stream
def generate_mjpeg():
    session = get_session()
    if not (session and session.isConnected()):
        return

    video = session.service("ALVideoDevice")
    nameId = video.subscribeCamera("mjpeg_stream", 2, 1, 11, 15)  # RGB, 320x240, 15fps

    try:
        while True:
            image = video.getImageRemote(nameId)
            if image is None:
                continue

            width = image[0]
            height = image[1]
            array = image[6]

            img_np = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
            img = Image.fromarray(img_np, 'RGB')

            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            frame = buf.getvalue()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.066)  # ~15 fps
    finally:
        video.unsubscribe(nameId)

@camera_routes.route('/pepper/camera/stream')
def camera_stream():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Analyse des doigts via serveur Vision externe
@camera_routes.route('/pepper/camera/count-fingers', methods=['POST'])
def count_fingers():
    session = get_session()
    if session is None or not session.isConnected():
        return jsonify({'success': False, 'error': 'Pepper non connecté'}), 400

    try:
        vision_ip = request.args.get('vision_ip', '127.0.0.1:5050')
        vision_url = 'http://{}/count-fingers'.format(vision_ip)

        video = session.service("ALVideoDevice")
        nameId = video.subscribeCamera("count_fingers_cam", 0, 1, 11, 30)

        image = video.getImageRemote(nameId)
        video.unsubscribe(nameId)

        if image is None:
            return jsonify({'success': False, 'error': 'Échec de capture'})

        width = image[0]
        height = image[1]
        array = image[6]

        img_np = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        cv2.imwrite(tmp.name, img_bgr)
        tmp.close()

        files = {'image': open(tmp.name, 'rb')}
        response = requests.post(vision_url, files=files)
        files['image'].close()

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'success': False, 'error': 'Vision: {}'.format(response.status_code)}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
