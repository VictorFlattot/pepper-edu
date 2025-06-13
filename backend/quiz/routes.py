# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, render_template
import json
import random
import os
import socket
from pepper.connection import get_session
from pepper.speech import start_recognition  # écoute libre avec comparaison directe

quiz_routes = Blueprint("quiz", __name__, template_folder="templates")

quiz_state = {
    "questions": [],
    "current_index": 0,
    "scores": {"Bleue": 0, "Rouge": 0},
    "current_team": "Bleue"
}

def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

@quiz_routes.route("/start", methods=["POST"])
def start_quiz():
    try:
        with open(os.path.join(os.path.dirname(__file__), "questions.json")) as f:
            questions = json.load(f)

        quiz_state["questions"] = random.sample(questions, min(len(questions), 10))
        quiz_state["current_index"] = 0
        quiz_state["scores"] = {"Bleue": 0, "Rouge": 0}
        quiz_state["current_team"] = "Bleue"

        session = get_session()
        if session and session.isConnected():
            tablet = session.service("ALTabletService")
            tts = session.service("ALTextToSpeech")
            tts.setLanguage("French")
            ip = get_host_ip()

            tablet.showWebview("http://{}:5000/tablet/show/quiz_rules".format(ip))

            regles = (
                u"Bienvenue dans le quiz. Voici les règles. "
                u"Le jeu oppose deux équipes, Bleue et Rouge.\\pau=300\\ "
                u"Chaque équipe répond à son tour à une question.\\pau=300\\ "
                u"Une bonne réponse rapporte un point.\\pau=300\\ "
                u"L'équipe avec le plus de points après 10 questions l'emporte.\\pau=300\\ "
                u"Les réponses sont \\pau=100\\ A, \\pau=100\\ B, \\pau=100\\ C \\pau=100\\ ou D."
            )

            tts.say(regles)

        return jsonify({"success": True})
    except Exception as e:
        print("Erreur start_quiz:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@quiz_routes.route("/state")
def quiz_state_route():
    index = quiz_state["current_index"]
    questions = quiz_state["questions"]

    if not questions:
        return jsonify({"status": "not_started"})
    if index >= len(questions):
        return jsonify({"status": "finished", "scores": quiz_state["scores"]})

    q = questions[index]
    return jsonify({
        "status": "running",
        "current_index": index,
        "question": q["question"],
        "choices": q["choices"],
        "answer": q["answer"],
        "scores": quiz_state["scores"],
        "current_team": quiz_state["current_team"]
    })

def advance_to_next_question():
    try:
        if quiz_state["current_index"] >= len(quiz_state["questions"]):
            return jsonify({"success": False, "error": "Fin du quiz"})

        session = get_session()
        if session and session.isConnected():
            tablet = session.service("ALTabletService")
            tts = session.service("ALTextToSpeech")
            animated_speech = session.service("ALAnimatedSpeech")
            motion = session.service("ALMotion")
            posture = session.service("ALRobotPosture")

            ip = get_host_ip()
            current = quiz_state["questions"][quiz_state["current_index"]]
            tablet.showWebview("http://{}:5000/quiz/tablet/show/quiz_tablet".format(ip))

            animated_config = {"bodyLanguageMode": "contextual"}
            motion.setStiffnesses("Body", 1.0)
            posture.goToPosture("StandInit", 0.6)

            current_team = quiz_state["current_team"]
            phrases = {
                "Bleue": [
                    u"C'est à l'équipe Bleue de répondre !",
                    u"L'équipe Bleue, préparez-vous !",
                    u"Bleue, à vous de jouer !",
                    u"À l'équipe Bleue de faire son choix !"
                ],
                "Rouge": [
                    u"C'est à l'équipe Rouge de répondre !",
                    u"L'équipe Rouge, préparez-vous !",
                    u"Rouge, à vous de jouer !",
                    u"À l'équipe Rouge de faire son choix !"
                ]
            }

            animated_speech.say(random.choice(phrases[current_team]).encode("utf-8"), animated_config)

            # 📢 Lecture de la question
            text = u"\\pau=400\\" + unicode(current["question"]) + u"\\pau=600\\"
            letters = ["A", "B", "C", "D"]
            for i, choice in enumerate(current["choices"]):
                text += u" {} : {}\\pau=500\\".format(letters[i], unicode(choice))
            animated_speech.say(text.encode("utf-8"), animated_config)

            # 🎤 Écoute vocale libre + comparaison directe
            expected_texts = current["choices"]
            correct_letter = current["answer"]
            start_recognition(expected_texts, correct_letter)

        return jsonify({"success": True})
    except Exception as e:
        print("Erreur next_question:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@quiz_routes.route("/next", methods=["POST"])
def next_question():
    return advance_to_next_question()

@quiz_routes.route("/tablet/show/<template_name>")
def show_quiz_template(template_name):
    index = quiz_state["current_index"]
    ip = get_host_ip()

    if template_name == "quiz_tablet":
        if index < 0 or index >= len(quiz_state["questions"]):
            return "Aucune question disponible"

        question = quiz_state["questions"][index]
        return render_template(
            "quiz_tablet.html",
            question=question["question"],
            choices=[(chr(65 + i), c) for i, c in enumerate(question["choices"])],
            scores=quiz_state["scores"],
            current_team=quiz_state["current_team"],
            server_ip=ip
        )
    elif template_name == "quiz_rules":
        return render_template("quiz_rules.html", server_ip=ip)
    elif template_name == "victory":
        team = request.args.get("team", "Bleue")
        bleue = int(request.args.get("bleue", 0))
        rouge = int(request.args.get("rouge", 0))
        color = "#007bff" if team == "Bleue" else "#dc3545"
        return render_template("victory.html", team=team, bleue=bleue, rouge=rouge, color=color, server_ip=ip)
    else:
        return "Template inconnu", 404

@quiz_routes.route("/answer", methods=["POST"])
def answer_question():
    try:
        data = request.get_json(force=True)
        choice = data.get("answer", "").upper().strip()
        if choice not in ["A", "B", "C", "D"]:
            return jsonify({"success": False, "error": "Réponse invalide"})

        current_index = quiz_state["current_index"]
        if current_index < 0 or current_index >= len(quiz_state["questions"]):
            return jsonify({"success": False, "error": "Aucune question active"})

        question = quiz_state["questions"][current_index]
        correct_answer = question["answer"].upper()
        current_team = quiz_state["current_team"]
        other_team = "Rouge" if current_team == "Bleue" else "Bleue"

        is_correct = (choice == correct_answer)

        session = get_session()
        tts = session.service("ALTextToSpeech") if session and session.isConnected() else None
        if tts:
            tts.setLanguage("French")

        if is_correct:
            quiz_state["scores"][current_team] += 1
            if tts:
                tts.say("{} a donné la bonne réponse !".format(current_team))
        else:
            if tts:
                tts.say("Ce n’était pas la bonne réponse.")

        quiz_state["current_team"] = other_team
        quiz_state["current_index"] += 1

        if quiz_state["current_index"] >= len(quiz_state["questions"]):
            bleue = quiz_state["scores"]["Bleue"]
            rouge = quiz_state["scores"]["Rouge"]

            if bleue == rouge:
                gagnant = u"Egalite"
                texte = u"Le quiz est terminé. Égalité parfaite. {} points partout !".format(bleue)
            else:
                gagnant = u"Bleue" if bleue > rouge else u"Rouge"
                texte = (
                    u"Le quiz est terminé. "
                    u"L’équipe Bleue a {} point{}. "
                    u"L’équipe Rouge a {} point{}. "
                    u"Félicitations à l’équipe {} qui remporte ce quiz !"
                ).format(
                    bleue, u"s" if bleue > 1 else u"",
                    rouge, u"s" if rouge > 1 else u"",
                    gagnant
                )

            if session and session.isConnected():
                animated = session.service("ALAnimatedSpeech")
                tablet = session.service("ALTabletService")
                ip = get_host_ip()
                tablet.showWebview("http://{}:5000/quiz/tablet/show/victory?team={}&bleue={}&rouge={}".format(ip, gagnant, bleue, rouge))
                animated.say(texte.encode("utf-8"), {"bodyLanguageMode": "contextual"})

            return jsonify({"success": True, "winner": gagnant})

        return jsonify({
            "success": True,
            "correct": is_correct,
            "current_team": quiz_state["current_team"]
        })

    except Exception as e:
        print("Erreur dans /answer :", e)
        return jsonify({"success": False, "error": str(e)})
