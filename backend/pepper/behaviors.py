# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
import json
import os
from pepper.connection import get_session

behavior_routes = Blueprint('behavior', __name__)

@behavior_routes.route('/get', methods=['GET'])
def get_behaviors():
    try:
        path = os.path.join(os.path.dirname(__file__), '.', 'behaviors.json')
        with open(path, 'r') as f:
            behaviors = json.load(f)
        return jsonify(behaviors)
    except Exception as e:
        print("Erreur lecture behaviors:", e)
        return jsonify({'error': str(e)}), 500

@behavior_routes.route('/run', methods=['POST'])
def run_behavior():
    behavior_id = request.args.get('id')
    session = get_session()

    if not behavior_id:
        return jsonify({'success': False, 'error': 'ID de comportement manquant'}), 400
    if session is None or not session.isConnected():
        return jsonify({'success': False, 'error': 'Session non connectée à Pepper'}), 400

    try:
        manager = session.service("ALBehaviorManager")
        if not manager.isBehaviorInstalled(behavior_id):
            return jsonify({'success': False, 'error': 'Comportement non installé sur Pepper'}), 404

        if manager.isBehaviorRunning(behavior_id):
            manager.stopBehavior(behavior_id)

        manager.runBehavior(behavior_id)
        return jsonify({'success': True})
    except Exception as e:
        print("Erreur lancement comportement:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@behavior_routes.route('/stop', methods=['POST'])
def stop_behavior():
    behavior_id = request.args.get('id')
    session = get_session()

    if not behavior_id:
        return jsonify({'success': False, 'error': 'ID manquant'}), 400
    if session is None or not session.isConnected():
        return jsonify({'success': False, 'error': 'Session non connectée'}), 400

    try:
        print("[BEHAVIOR] Tentative d'arrêt : {}".format(behavior_id))
        manager = session.service("ALBehaviorManager")

        if manager.isBehaviorRunning(behavior_id):
            manager.stopBehavior(behavior_id)
            print("[BEHAVIOR] Comportement arrêté")

        try:
            motion = session.service("ALMotion")
            posture = session.service("ALRobotPosture")
            motion.setStiffnesses("Body", 1.0)
            posture.goToPosture("StandInit", 0.5)
            print("[BEHAVIOR] Position par défaut appliquée")
        except Exception as e:
            print("[BEHAVIOR] Erreur retour position par défaut :", e)

        return jsonify({'success': True})

    except Exception as e:
        print("Erreur arrêt comportement:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@behavior_routes.route('/status', methods=['GET'])
def pepper_status_id():
    check_id = request.args.get('check')
    session = get_session()
    connected = session is not None and session.isConnected()
    result = {'connected': connected}

    if check_id and connected:
        try:
            manager = session.service("ALBehaviorManager")
            running_behaviors = manager.getRunningBehaviors()
            result['running'] = check_id in running_behaviors
        except Exception as e:
            print("Erreur récupération comportement actif:", e)
            result['running'] = False

    return jsonify(result)

@behavior_routes.route('/running', methods=['GET'])
def pepper_running_behaviors():
    session = get_session()
    if session is None or not session.isConnected():
        return jsonify({'running': []})

    try:
        manager = session.service("ALBehaviorManager")
        running = manager.getRunningBehaviors()
        return jsonify({'running': running})
    except Exception as e:
        print("Erreur récupération comportements actifs:", e)
        return jsonify({'running': [], 'error': str(e)})

@behavior_routes.route('/generate', methods=['POST'])
def generate_behaviors_file():
    session = get_session()
    if session is None or not session.isConnected():
        return jsonify({'success': False, 'error': 'Pepper non connecté'}), 400

    try:
        manager = session.service("ALBehaviorManager")
        behaviors = manager.getInstalledBehaviors()

        generated = []
        for b in behaviors:
            last_segment = b.strip("/").split("/")[-1]
            generated.append({ "id": b, "name": last_segment })

        save_path = os.path.join(os.path.dirname(__file__), '.', 'behaviors_gen.json')
        with open(save_path, 'w') as f:
            json.dump(generated, f, indent=2)

        return jsonify({'success': True, 'count': len(generated)})
    except Exception as e:
        print("Erreur génération behaviors.json:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@behavior_routes.route('/list', methods=['GET'])
def list_behaviors():
    try:
        file_path = os.path.join(os.path.dirname(__file__), '.', 'behaviors_gen.json')
        with open(file_path, 'r') as f:
            behaviors = json.load(f)
        return jsonify(behaviors)
    except Exception as e:
        print("Erreur lecture behaviors_gen.json:", e)
        return jsonify({'error': str(e)}), 500      