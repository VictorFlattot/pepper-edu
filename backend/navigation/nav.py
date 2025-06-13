# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, send_file
from pepper.connection import get_session
import os, json
import numpy as np
from PIL import Image
import io
from naoqi import ALProxy

nav_routes = Blueprint('navigation', __name__)

SLAM_MAPS_PATH = os.path.join(os.path.dirname(__file__), '.', 'slam_maps.json')

def read_slam_maps():
    if not os.path.exists(SLAM_MAPS_PATH):
        return []
    try:
        with open(SLAM_MAPS_PATH, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("⚠️ Format invalide dans slam_maps.json")
                return []
    except Exception as e:
        print("❌ Erreur lecture slam_maps.json :", e)
        return []

def write_slam_maps(maps):
    try:
        with open(SLAM_MAPS_PATH, "w") as f:
            json.dump(maps, f, indent=2)
    except Exception as e:
        print("❌ Erreur écriture slam_maps.json :", e)

@nav_routes.route("/slam/maps", methods=["GET"])
def get_slam_maps():
    return jsonify(read_slam_maps())

@nav_routes.route("/slam/select", methods=["POST"])
def nav_slam_select():
    try:
        data = request.get_json()
        name = data.get("map") or data.get("name")

        if not name:
            return jsonify({"success": False, "error": "Paramètre 'map' manquant."}), 400

        session = get_session()
        if not session or not session.isConnected():
            return jsonify({"success": False, "error": "Connexion à Pepper échouée."}), 500

        session.service("ALMemory").insertData("Exploration/Selected", name)
        print("✅ Carte SLAM sélectionnée :", name)
        return jsonify({"success": True, "selected": name})
    except Exception as e:
        print("❌ Erreur dans /slam/select :", e)
        return jsonify({"success": False, "error": str(e)}), 500

@nav_routes.route("/slam/maps/label", methods=["POST"])
def update_slam_map_label():
    try:
        data = request.get_json()
        name = data.get("name")
        label = data.get("label", "")

        if not name:
            return jsonify({"success": False, "error": "Paramètre 'name' requis"}), 400

        cartes = read_slam_maps()
        updated = False
        for m in cartes:
            if m.get("name") == name:
                m["label"] = label
                updated = True
                break

        if not updated:
            return jsonify({"success": False, "error": "Carte non trouvée"}), 404

        write_slam_maps(cartes)
        print("✅ Label mis à jour pour :", name, "→", label)
        return jsonify({"success": True})
    except Exception as e:
        print("❌ Erreur update label :", e)
        return jsonify({"success": False, "error": str(e)}), 500

@nav_routes.route("/slam/maps/delete", methods=["POST"])
def delete_slam_map():
    try:
        data = request.get_json()
        name = data.get("name")

        if not name:
            return jsonify({"success": False, "error": "Nom manquant"}), 400

        cartes = read_slam_maps()
        cartes = [c for c in cartes if c.get("name") != name]
        write_slam_maps(cartes)

        print("🗑️ Carte supprimée :", name)
        return jsonify({"success": True})
    except Exception as e:
        print("❌ Erreur suppression carte :", e)
        return jsonify({"success": False, "error": str(e)}), 500

@nav_routes.route("/slam/image/<map_name>", methods=["GET"])
def slam_image(map_name):
    try:
        session = get_session()
        if not session or not session.isConnected():
            return "Pepper non connecté", 500

        navigation = session.service("ALNavigation")
        navigation.loadExploration(map_name)
        result = navigation.getMetricalMap()
        resolution, width, height, data = result[0], result[1], result[2], result[4]

        raw = np.array(data).reshape((width, height))
        img = (100 - raw) * 2.55
        img = np.clip(img, 0, 255).astype(np.uint8)
        pil_img = Image.fromarray(img, mode='L').transpose(Image.FLIP_TOP_BOTTOM)

        buffer = io.BytesIO()
        pil_img.save(buffer, format='PNG')
        buffer.seek(0)

        return send_file(buffer, mimetype='image/png')
    except Exception as e:
        print("❌ Erreur génération image carte :", e)
        return "Erreur interne", 500
