# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
import qi

pepper_routes = Blueprint('pepper', __name__)
pepper_session = None
autoriser_reconnexion = False

def ensure_pepper_connected(ip=None, port=None, max_attempts=3):
    global pepper_session
    pepper_ip = ip or '11.255.255.100'
    pepper_port = int(port or 9559)

    if pepper_session and pepper_session.isConnected():
        return True

    for attempt in range(1, max_attempts + 1):
        try:
            print("🔁 Tentative de connexion #{} à Pepper...".format(attempt))
            session = qi.Session()
            session.listen("tcp://0.0.0.0:0")
            session.connect("tcp://{}:{}".format(pepper_ip, pepper_port))

            if session.isConnected():
                pepper_session = session
                print("✅ Connexion réussie à Pepper")
                return True
        except Exception as e:
            print("❌ Échec tentative {}: {}".format(attempt, e))

    pepper_session = None
    return False


@pepper_routes.route('/connect', methods=['GET'])
def connect_pepper():
    global autoriser_reconnexion
    ip = request.args.get('ip', '11.255.255.100')
    port = request.args.get('port', 9559)

    success = ensure_pepper_connected(ip, port)
    autoriser_reconnexion = success

    if success:
        print("✅ Session enregistrée pour Pepper à {}:{}".format(ip, port))
    else:
        print("❌ Connexion refusée")

    return jsonify({'connected': success})


@pepper_routes.route('/status', methods=['GET'])
def pepper_status():
    connected = pepper_session is not None and pepper_session.isConnected()
    # print("🔎 Statut session Pepper :", connected)
    return jsonify({'connected': connected})


@pepper_routes.route('/disconnect', methods=['POST'])
def disconnect_pepper():
    global pepper_session, autoriser_reconnexion
    try:
        if pepper_session and pepper_session.isConnected():
            pepper_session.close()
            print("🔌 Session Pepper fermée proprement")

        pepper_session = None
        autoriser_reconnexion = False
        return jsonify({'disconnected': True})
    except Exception as e:
        print("❌ Erreur lors de la déconnexion :", e)
        return jsonify({'disconnected': False, 'error': str(e)}), 500


@pepper_routes.route('/test', methods=['GET'])
def test_pepper_alive():
    session = get_session()
    if session and session.isConnected():
        return jsonify({'status': 'connected'})
    return jsonify({'status': 'disconnected'})


@pepper_routes.route('/keepalive', methods=['GET'])
def keep_pepper_alive():
    try:
        session = get_session()
        if session and session.isConnected():
            memory = session.service("ALMemory")
            memory.getData("Device/DeviceList")  # Juste une requête simple
            return jsonify({'alive': True})
    except Exception as e:
        print("❌ Erreur keepalive :", e)

    return jsonify({'alive': False})


def get_session():
    return pepper_session
