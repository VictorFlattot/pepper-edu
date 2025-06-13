# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from pepper.connection import get_session
import socket, json, os

memory_routes = Blueprint("memory", __name__)
RESULTS_PATH = "/tmp/total_sante_resultats.json"
SLAM_MAPS_PATH = os.path.join(os.path.dirname(__file__),'../navigation', 'slam_maps.json')

# 🔹 Détecte l'IP locale automatiquement
def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

# 🔹 Enregistre l'IP du backend dans ALMemory
@memory_routes.route("/memory/set_server_ip", methods=["POST"])
def set_server_ip():
    try:
        ip = request.args.get("ip") or get_host_ip()
        session = get_session()
        if session and session.isConnected():
            session.service("ALMemory").insertData("App/ServerIP", ip)
            return jsonify({"success": True, "ip": ip})
        return jsonify({"success": False, "error": "Session non connectée"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 🔹 Récupère l'IP enregistrée
@memory_routes.route("/memory/get_server_ip")
def get_server_ip():
    try:
        session = get_session()
        if session and session.isConnected():
            ip = session.service("ALMemory").getData("App/ServerIP")
            return jsonify({"success": True, "ip": ip})
        return jsonify({"success": False, "error": "Session non connectée"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 🔹 Renvoie le fichier JSON de résultats
@memory_routes.route("/memory/get_resultats_total_sante")
def get_resultats_total_sante():
    try:
        if not os.path.exists(RESULTS_PATH):
            return jsonify({"success": False, "error": "Aucun résultat enregistré"}), 404
        with open(RESULTS_PATH) as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@memory_routes.route("/memory/set_resultat_total_sante", methods=["POST"])
def set_resultat_total_sante():
    try:
        raw = request.get_json(force=True)
        if not raw:
            return jsonify({"status": "error", "message": "Données manquantes"}), 400

        prenom = list(raw.keys())[0]
        data = raw[prenom]

        # Charger fichier existant
        if os.path.exists(RESULTS_PATH):
            with open(RESULTS_PATH, "r") as f:
                anciens = json.load(f)
        else:
            anciens = {}

        # Mettre à jour ou ajouter
        anciens[prenom] = data

        with open(RESULTS_PATH, "w") as f:
            json.dump(anciens, f, indent=2)

        print("✅ Données enregistrées pour", prenom)
        return jsonify({"status": "ok"})
    except Exception as e:
        print("❌ Erreur set_resultat_total_sante:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# 🔹 Handler d'abonnement à l'événement ALMemory
class PepperMemoryHandler(object):
    def onResultat(self, key, value, msg):
        try:
            raw = json.loads(value)
            prenom = raw.get("total_sante_prenom", "inconnu")
            ordre = [
                "tension", "ldl", "chol", "hdl", "tg", "hba1c", "gly", "tt", "tabac"
            ]

            # Initialisation vide
            struct = {prenom: {}}
            total = 0

            for nom in ordre:
                struct[prenom][nom] = {}

            # Remplissage structuré
            for k, v in raw.items():
                if k == "total_sante_prenom":
                    continue
                if k.startswith("total_sante_"):
                    champ = k[len("total_sante_"):]
                    if "_" in champ:
                        nom, souschamp = champ.split("_", 1)
                        souschamp = "points" if souschamp == "points" else "valeur"
                    else:
                        nom, souschamp = champ, "valeur"

                    if nom in struct[prenom]:
                        struct[prenom][nom][souschamp] = v
                        if souschamp == "points":
                            try:
                                total += int(v)
                            except:
                                pass

            # Ajout du total
            struct[prenom]["total"] = total

            try:
                # Charger l'existant s'il y en a un
                if os.path.exists(RESULTS_PATH):
                    with open(RESULTS_PATH, "r") as f:
                        anciens = json.load(f)
                else:
                    anciens = {}

                # Fusionner ou remplacer les données du prénom courant
                anciens[prenom] = struct[prenom]

                # Réécriture du fichier avec les données mises à jour
                with open(RESULTS_PATH, "w") as f:
                    json.dump(anciens, f, indent=2)

                print("✅ Données ajoutées pour", prenom)
            except Exception as e:
                print("❌ Erreur lors de l'écriture cumulative :", e)

            print("✅ Données restructurées et enregistrées.")
        except Exception as e:
            print("❌ Erreur structuration Python :", e)
# 🔹 Abonnement à l'événement ALMemory
@memory_routes.route("/memory/subscribe_resultats", methods=["POST"])
def subscribe_route():
    try:
        session = get_session()
        if session and session.isConnected():
            almemory = session.service("ALMemory")

            try:
                # Clean previous
                if "python_memory" in session.services():
                    print("🔁 python_memory déjà présent, on supprime.")
                    session.unregisterService("python_memory")
            except Exception as e:
                print("⚠️ Problème au unregister :", e)

            global memory_handler

            try:
                memory_handler = PepperMemoryHandler()
                session.registerService("python_memory", memory_handler)
                print("✅ Service python_memory inscrit.")
            except Exception as e:
                print("❌ Erreur registerService :", e)
            almemory.subscribeToEvent("TotalSante/ResultatFinal", "python_memory", "onResultat")
        print("✅ Abonnement actif")
        return jsonify({"success": True})
    except Exception as e:
        print("❌ Erreur abonnement :", e)
        return jsonify({"success": False, "error": str(e)}), 500

@memory_routes.route("/memory/delete_resultat_total_sante/<prenom>", methods=["DELETE"])
def delete_resultat_total_sante(prenom):
    try:
        if os.path.exists(RESULTS_PATH):
            with open(RESULTS_PATH, "r") as f:
                data = json.load(f)
            if prenom in data:
                del data[prenom]
                with open(RESULTS_PATH, "w") as f:
                    json.dump(data, f, indent=2)
                return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "Participant non trouvé"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🔹 Handler d'abonnement à l'événement ALMemory pour la carte SLAM
class SlamMapMemoryHandler(object):
    def onMapInfo(self, key, value, msg):
        try:
            name = str(value).strip()
            if not name:
                print("❌ Nom de carte vide.")
                return

            # Chargement sécurisé
            if os.path.exists(SLAM_MAPS_PATH):
                with open(SLAM_MAPS_PATH, "r") as f:
                    try:
                        cartes = json.load(f)
                        if not isinstance(cartes, list) or not all(isinstance(m, dict) and "name" in m for m in cartes):
                            print("⚠️ Contenu JSON non structuré, réinitialisation.")
                            cartes = []
                    except ValueError:
                        print("⚠️ JSON vide ou invalide, réinitialisation.")
                        cartes = []
            else:
                cartes = []

            # Ajouter si non déjà présent
            if not any(m.get("name") == name for m in cartes):
                cartes.append({"label": "", "name": name})
                with open(SLAM_MAPS_PATH, "w") as f:
                    json.dump(cartes, f, indent=2)
                print("✅ Carte ajoutée :", name)
            else:
                print("ℹ️ Carte déjà enregistrée :", name)

        except Exception as e:
            print("❌ Erreur dans onMapInfo :", e)

# 🔹 Abonnement à l’événement
@memory_routes.route("/memory/subscribe_slam_map", methods=["POST"])
def subscribe_slam_map():
    try:
        session = get_session()
        if session and session.isConnected():
            almemory = session.service("ALMemory")

            # clean + register
            try:
                if "slam_memory" in session.services():
                    session.unregisterService("slam_memory")
            except:
                pass

            global slam_memory_handler
            slam_memory_handler = SlamMapMemoryHandler()
            session.registerService("slam_memory", slam_memory_handler)
            almemory.subscribeToEvent("Exploration/LastMapName", "slam_memory", "onMapInfo")

            return jsonify({"success": True})  # ✅ RETURN OBLIGATOIRE ICI
        else:
            return jsonify({"success": False, "error": "Session non connectée"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

