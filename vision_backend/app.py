from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np

app = Flask(__name__)
CORS(app)

# Initialisation Mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=True, max_num_hands=1, model_complexity=1,
                      min_detection_confidence=0.5)
tipIds = [4, 8, 12, 16, 20]

@app.route('/ping')
def ping():
    return jsonify({"success": True, "message": "Vision OK"})

@app.route('/count-fingers', methods=['POST'])
def count_fingers():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "Aucune image reçue"}), 400

    try:
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        fingers_up = 0

        if results.multi_hand_landmarks:
            handLms = results.multi_hand_landmarks[0]
            lmList = []
            h, w, _ = img.shape
            for id, lm in enumerate(handLms.landmark):
                px, py = int(lm.x * w), int(lm.y * h)
                lmList.append((px, py))

            if lmList:
                # Pouce
                if lmList[tipIds[0]][0] > lmList[tipIds[0] - 1][0]:
                    fingers_up += 1
                # 4 autres doigts
                for i in range(1, 5):
                    if lmList[tipIds[i]][1] < lmList[tipIds[i] - 2][1]:
                        fingers_up += 1

        return jsonify({"success": True, "fingers": fingers_up})

    except Exception as e:
        print("❌ Erreur traitement image :", e)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
