# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, render_template
from pepper.connection import get_session
import socket, time

tablet_routes = Blueprint("tablet", __name__)

def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

@tablet_routes.route('/show/<page_name>', methods=['GET'])
def show_static_from_backend(page_name):
    try:
        safe_name = page_name.replace("..", "").replace("/", "")
        timestamp = int(time.time())
        url = "http://{}:5000/static/{}.html?t={}".format(get_host_ip(), safe_name,timestamp)

        session = get_session()
        if session and session.isConnected():
            tablet = session.service("ALTabletService")
            tablet.hideWebview()
            tablet.loadUrl(url)
            tablet.showWebview(url)
            return jsonify({"success": True, "url": url})
        else:
            return jsonify({"success": False, "error": "Pepper non connecté"}), 400
    except Exception as e:
        print("Erreur affichage page tablette :", e)
        return jsonify({"success": False, "error": str(e)}), 500

from flask import Response, request

@tablet_routes.route('/generate_config_js', methods=['POST'])
def generate_config_js():
    try:
        data = request.get_json(force=True)
        ip = data.get('ip', '127.0.0.1')
        port = int(data.get('port', 5000))

        content = 'window.BACKEND_IP = "{}";\nwindow.BACKEND_PORT = {};'.format(ip, port)
        with open('static/config.js', 'w') as f:
            f.write(content)

        return jsonify({"success": True})
    except Exception as e:
        print("Erreur génération config.js :", e)
        return jsonify({"success": False, "error": str(e)}), 500

@tablet_routes.route('/render/<template_name>', methods=["GET"])
def show_template_page(template_name):
    try:
        session = get_session()
        if not session or not session.isConnected():
            return jsonify({"success": False, "error": "Pepper non connecté"}), 400

        # Rendu Jinja sans injection d'IP
        context = {}  # Tu peux ajouter ici des données spécifiques par template si besoin
        html_rendered = render_template(template_name + ".html", **context)

        # Sauvegarde temporaire dans static/
        timestamp = int(time.time())
        rendered_path = "static/rendered_" + template_name + ".html"
        with open(rendered_path, "w") as f:
            f.write(html_rendered.encode("utf-8"))

        url = "http://{}:5000/static/rendered_{}.html?t={}".format(get_host_ip(), template_name, timestamp)
        tablet = session.service("ALTabletService")
        tablet.hideWebview()
        tablet.loadUrl(url)
        tablet.showWebview(url)

        return jsonify({"success": True, "url": url})

    except Exception as e:
        print("Erreur affichage page tablette dynamique:", e)
        return jsonify({"success": False, "error": str(e)}), 500
