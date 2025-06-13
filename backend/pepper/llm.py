# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
import requests
import re
import json
import random
import threading
from pepper.connection import get_session

llm_routes = Blueprint("llm", __name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

SYSTEM_PROMPT = u"""
Tu es Pepper, un petit robot sympathique qui aide pendant des séances d’éducation sur le diabète. 
Tu parles en français, de manière simple, avec des phrases courtes et faciles à comprendre. 
Tu réponds calmement, sans jargon médical, et tu encourages les personnes à bien gérer leur santé. 

Reste toujours positif et bienveillant.
"""

def speak_async(session, text):
    def run():
        try:
            tts = session.service("ALTextToSpeech")
            animated = session.service("ALAnimatedSpeech")
            tts.setLanguage("French")
            animated.say("\\rspd=85\\ " + text)
        except Exception as e:
            print("❌ Erreur TTS :", str(e))
    threading.Thread(target=run).start()


@llm_routes.route("/ask", methods=["POST"])
def ask_pepper_stream():
    try:
        data = request.get_json(force=True)
        question = data.get("prompt", "").strip()
        if not question:
            return jsonify({"error": "Prompt vide"}), 400

        prompt = SYSTEM_PROMPT + "\nUtilisateur : " + question + "\nPepper :"

        session = get_session()
        if not session or not session.isConnected():
            print("❌ Pepper non connecté")
            return jsonify({"error": "Pepper non connecté"}), 503

        # 🔸 Phrases d’introduction aléatoires
        phrases_generiques = [""]
        phrases_demande = [""]
        motcles_demande = ["explique", "dis-moi", "c’est quoi", "qu’est-ce que", "qu'est ce que", "raconte", "décris"]

        lower_question = question.lower()
        if any(m in lower_question for m in motcles_demande):
            phrase_intro = random.choice(phrases_demande)
        else:
            phrase_intro = random.choice(phrases_generiques)

        if phrase_intro:
            speak_async(session, phrase_intro)

        # 🔁 Appel au modèle Ollama
        res = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": True},
            stream=True,
            timeout=60
        )

        full_response = ""
        buffer = ""
        sentence_regex = re.compile(r'(.+?[.!?…‽])(\s|$)')

        for line in res.iter_lines():
            if not line:
                continue
            try:
                line_text = line.decode("utf-8").strip()

                if line_text.startswith("data:"):
                    line_text = line_text[5:].strip()

                payload = json.loads(line_text)
                chunk = payload.get("response", "")
                if not chunk:
                    continue

                full_response += chunk
                buffer += chunk

                while True:
                    match = sentence_regex.search(buffer)
                    if not match:
                        break

                    sentence = match.group(1).strip()
                    speak_async(session, sentence)
                    buffer = buffer[match.end():]

            except Exception as e:
                print("❌ Erreur dans boucle :", str(e))

        if buffer.strip():
            speak_async(session, buffer.strip())

        # 🔁 Retour à la posture par défaut
        try:
            posture = session.service("ALRobotPosture")
            posture.goToPosture("StandInit", 0.5)
        except Exception as e:
            print("❌ Erreur retour posture :", str(e))

        print("✅ Réponse complète :", full_response.strip())
        if not full_response.strip():
            return jsonify({"error": "Réponse vide du LLM"}), 500

        return jsonify({"response": full_response.strip()})

    except Exception as e:
        print("❌ Erreur générale :", str(e))
        return jsonify({"error": "Erreur serveur", "details": str(e)}), 500
