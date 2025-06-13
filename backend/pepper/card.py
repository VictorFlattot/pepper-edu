# -*- coding: utf-8 -*-
import os
import json
from flask import Blueprint, jsonify, abort

card_routes = Blueprint('card_routes', __name__)

CARTE_JSON_PATH = os.path.join(os.path.dirname(__file__), 'cartes_actions.json')

def load_cartes():
    try:
        with open(CARTE_JSON_PATH) as f:
            content = f.read().decode('utf-8')
            return json.loads(content)
    except Exception as e:
        print("❌ Erreur chargement JSON cartes :", e)
        return []

@card_routes.route('/list', methods=['GET'])
def get_all_cartes():
    """Retourne toutes les cartes."""
    cartes = load_cartes()
    return jsonify(cartes)

@card_routes.route('/get/<int:numero>', methods=['GET'])
def get_carte_by_numero(numero):
    """Retourne une carte spécifique par son numéro."""
    cartes = load_cartes()
    for carte in cartes:
        if carte.get("numero") == numero:
            return jsonify(carte)
    abort(404)
