# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from pepper.connection import get_session
import time

move_routes = Blueprint('move', __name__)

@move_routes.route('/pepper/move', methods=['POST'])
def move_pepper():
    session = get_session()
    if session is None or not session.isConnected():
        return jsonify({'success': False, 'error': 'Pepper non connecté'}), 400

    try:
        data = request.get_json()
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))
        theta = float(data.get('theta', 0))

        motion = session.service("ALMotion")

        # ✅ Active les bras pendant la marche
        motion.setMoveArmsEnabled(True, True)
        motion.setWalkArmsEnabled(True, True)

        # ✅ Configuration "humaine"
        config = [
            ["MaxVelXY", 0.6],
            ["MaxVelTheta", 0.6],
            ["MaxAccXY", 0.5],
            ["MaxAccTheta", 0.5],
            ["TorsoWy", 0.1]
        ]

        motion.moveToward(x, y, theta, config)

        return jsonify({'success': True})
    except Exception as e:
        print("Erreur déplacement Pepper:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@move_routes.route('/pepper/stop', methods=['POST'])
def stop_pepper():
    session = get_session()
    if session is None or not session.isConnected():
        return jsonify({'success': False, 'error': 'Pepper non connecté'}), 400

    try:

        motion = session.service("ALMotion")
        posture = session.service("ALRobotPosture")

        motion.stopMove()
        time.sleep(0.1)
        motion.stopMove()

        # Optionnel : repositionne proprement
        posture.goToPosture("StandInit", 0.6)

        return jsonify({'success': True})
    except Exception as e:
        print("Erreur arrêt:", e)
        return jsonify({'success': False, 'error': str(e)}), 500
