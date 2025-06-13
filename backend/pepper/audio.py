# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Blueprint, request, jsonify
from pepper.connection import get_session
import time, requests, threading


audio_routes = Blueprint('audio', __name__)
rotation_active = False

def loop_rotate_eyes(session):
    global rotation_active
    leds = session.service("ALLeds")
    leds.setIntensity("FaceLeds", 1.0)
    while rotation_active:
        leds.rotateEyes(0x0000FF, 1.0, 3.0)  # 🔵 bleu, tourne 3s
        time.sleep(2.8)  # relance juste avant la fin


@audio_routes.route('/pepper/set-volume', methods=['POST'])
def set_volume():
    try:
        data = request.get_json()
        volume = data.get('volume')

        if volume is None or not (0 <= volume <= 100):
            return jsonify({"success": False, "error": "Volume invalide"}), 400

        session = get_session()
        if session and session.isConnected():
            audio = session.service("ALAudioDevice")
            audio.setOutputVolume(int(volume))  # ici volume général du robot
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Pepper non connecté"}), 500

    except Exception as e:
        print("[Erreur set-volume]", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@audio_routes.route("/chat_vocal", methods=["POST"])
def chat_vocal():
    global rotation_active

    try:
        session = get_session()
        if not session or not session.isConnected():
            return jsonify({"error": "Pepper non connecté"}), 503

        sr = session.service("SpeechRecognition")
        memory = session.service("ALMemory")
        tts = session.service("ALTextToSpeech")
        leds = session.service("ALLeds")
        tts.setLanguage("French")

        try:
            sr.stop()
            time.sleep(0.5)
        except:
            pass

        sr.setLanguage("fr-fr")
        sr.enableAutoDetection()
        sr.setHoldTime(5)
        sr.setIdleReleaseTime(5)
        sr.setMaxRecordingDuration(10)
        sr.setLookaheadDuration(0.5)
        sr.setAutoDetectionThreshold(5)

        # 🔄 rotation des yeux pendant l'écoute
        rotation_active = True
        threading.Thread(target=loop_rotate_eyes, args=(session,)).start()

        print("🎤 Démarrage écoute...")
        sr.start()
        time.sleep(0.3)
        time.sleep(20)  # écoute max 10s, s'arrête avant si silence (idleReleaseTime)
        sr.stop()
        time.sleep(0.3)
        rotation_active = False

        result_text = ""
        for _ in range(10):  # 10 x 200ms = 2s
            try:
                result = memory.getData("SpeechRecognition")
                memory.removeData("SpeechRecognition")
                result_text = result.strip()
                print(u"🗣️ Reçu après arrêt :", result_text)
                break
            except RuntimeError:
                time.sleep(0.2)

        if not result_text:
            print("❌ Aucune phrase reconnue")

        leds.fadeRGB("FaceLeds", 0xFFFFFF, 0.3)  # 🤍 retour à normal

        if not result_text:
            return jsonify({"error": "Aucune réponse reconnue"}), 400

        # 🧠 Envoie au LLM
        r = requests.post("http://localhost:5000/llm/ask", json={"prompt": result_text})
        print(u"📤 Réponse LLM brute : {}".format(r.content.decode("utf-8", errors="replace")))

        if not r.ok:
            return jsonify({"error": "Erreur LLM"}), 500

        response = r.json().get("response", "").strip()
        if not response:
            return jsonify({"error": "Réponse vide du LLM"}), 500

        return jsonify({"question": result_text, "response": response})

    except Exception as e:
        print("❌ Erreur :", str(e))
        return jsonify({"error": "Erreur interne", "details": str(e)}), 500

