# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from pepper.connection import get_session
import threading
import time
import os
import requests
from naoqi import ALProxy

speech_routes = Blueprint("speech", __name__)

def send_answer(answer_letter):
    try:
        server_ip = request.host  # ex: 127.0.0.1:5000
        url = "http://{}/quiz/answer".format(server_ip)
        print("📤 Envoi de la réponse '{}' à {}".format(answer_letter, url))
        r = requests.post(url, json={"answer": answer_letter})
        print("✅ Résultat :", r.json())
    except Exception as e:
        print("❌ Erreur d'envoi :", e)

def start_recognition(expected_answers, correct_letter, confidence=0.35):
    thread = threading.Thread(
        target=_recognize_loop,
        args=(expected_answers, correct_letter, confidence)
    )
    thread.start()

def _recognize_loop(expected_answers, correct_letter, confidence):
    session = get_session()
    if not session or not session.isConnected():
        print("❌ Pas de session Pepper.")
        return

    try:
        sr = session.service("SpeechRecognition")
        memory = session.service("ALMemory")

        sr.setLanguage("fr-fr")
        sr.enableAutoDetection()
        sr.setHoldTime(2.5)
        sr.setIdleReleaseTime(1.0)
        sr.setMaxRecordingDuration(10)
        sr.setLookaheadDuration(0.5)
        sr.setAutoDetectionThreshold(5)

        print("🎤 Démarrage de la reconnaissance vocale...")
        sr.start()

        expected = [x.lower().strip() for x in expected_answers]
        timeout = 15  # secondes max d'écoute
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = memory.getData("SpeechRecognition")
            if result:
                print("🗣️ Reçu :", result)
                recognized = result.lower().strip()
                if recognized in expected:
                    print("✅ Réponse reconnue :", recognized)
                    send_answer(correct_letter)
                    return
                else:
                    print("❌ Mauvaise réponse :", recognized)
            time.sleep(0.5)

        print("⏹️ Fin d'écoute (timeout)")
        sr.stop()

    except Exception as e:
        print("❌ Erreur reco :", e)

@speech_routes.route("/say", methods=["POST"])
def pepper_say():
    data = request.get_json()
    text = data.get('text', '')
    session = get_session()
    if session is None or not session.isConnected():
        return jsonify({'success': False, 'error': 'Pepper non connecté'}), 400

    tts = session.service("ALTextToSpeech")
    tts.setLanguage("French")
    tts.say(text)
    return jsonify({'success': True})