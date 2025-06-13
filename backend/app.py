#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
import logging
from flask_cors import CORS
from pepper.connection import pepper_routes
from pepper.behaviors import behavior_routes
from quiz.routes import quiz_routes
from pepper.move import move_routes
from pepper.autonomy import autonomy_routes
from pepper.audio import audio_routes
from navigation.nav import nav_routes
from tablet.tablet import tablet_routes
from pepper.llm import llm_routes
from pepper.speech import speech_routes
from pepper.camera import camera_routes
from pepper.memory import memory_routes
from pepper.card import card_routes
# Récupère le logger Flask par défaut
log = logging.getLogger('werkzeug')

app = Flask(__name__, static_url_path='/static')
CORS(app)

app.register_blueprint(pepper_routes, url_prefix='/pepper')
app.register_blueprint(behavior_routes, url_prefix='/behavior')
app.register_blueprint(quiz_routes, url_prefix='/quiz')
app.register_blueprint(nav_routes, url_prefix='/nav')
app.register_blueprint(move_routes)
app.register_blueprint(autonomy_routes)
app.register_blueprint(audio_routes)
app.register_blueprint(tablet_routes, url_prefix='/tablet')
app.register_blueprint(llm_routes, url_prefix="/llm")
app.register_blueprint(speech_routes)
app.register_blueprint(camera_routes)
app.register_blueprint(memory_routes)
app.register_blueprint(card_routes, url_prefix='/card')


# Logger de Flask/Werkzeug
log = logging.getLogger('werkzeug')

HIDDEN_LOGS = ['/pepper/status', '/quiz/state']

class FilterStatusLogs(logging.Filter):
    def filter(self, record):
        try:
            msg = record.getMessage()
            for path in HIDDEN_LOGS:
                if path in msg:
                    return False  # ❌ Masque cette ligne
        except:
            pass
        return True  # ✅ Garde les autres
       
log.addFilter(FilterStatusLogs())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
