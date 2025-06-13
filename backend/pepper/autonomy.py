# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from pepper.connection import get_session

autonomy_routes = Blueprint('autonomy', __name__)

@autonomy_routes.route('/pepper/autonomy', methods=['POST'])
def set_autonomy_mode():
    session = get_session()
    if session is None or not session.isConnected():
        return jsonify({'success': False, 'error': 'Pepper non connecté'}), 400

    try:
        data = request.get_json()
        mode = data.get('mode')

        if mode not in ["interactive", "solitary", "disabled"]:
            return jsonify({'success': False, 'error': 'Mode invalide'}), 400

        life = session.service("ALAutonomousLife")
        motion = session.service("ALMotion")
        posture = session.service("ALRobotPosture")
        awareness = session.service("ALBasicAwareness")
        # if mode == "disabled":
        #     life.setState("disabled")
        #     motion.setStiffnesses("Body", 1.0)
        #     motion.setAngles(["HeadYaw", "HeadPitch"], [0.0, 0.0], 0.2)
        #     posture.goToPosture("StandInit", 0.5)
        # else:
        if mode == "interactive" :
            awareness.setTrackingMode("Head")
            awareness.setEngagementMode("FullyEngaged")

        life.setState(mode)

        return jsonify({'success': True, 'state': mode})
    except Exception as e:
        print("Erreur autonomie Pepper:", e)
        return jsonify({'success': False, 'error': str(e)}), 500
