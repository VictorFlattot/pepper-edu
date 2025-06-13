#!/bin/bash

# Dossier de base
BASE_DIR=~/victor_pepper

# Lancer frontend React
echo "🚀 Lancement du frontend React..."
gnome-terminal --title="🖥️ React Frontend" -- bash -c "cd $BASE_DIR/frontend && npm run dev -- --host; exec bash"

# Lancer backend Flask Pepper (Python 2.7)
echo "🤖 Lancement du backend Flask Pepper..."
gnome-terminal --title="🤖 Pepper Backend (Python 2.7)" -- bash -c "source $BASE_DIR/pepper_env/bin/activate && cd $BASE_DIR/backend && python2.7 app.py; exec bash"

# Lancer serveur Vision (Python 3)
echo "🧠 Lancement du backend Vision..."
gnome-terminal --title="🧠 Vision Backend (Python 3)" -- bash -c "source $BASE_DIR/vision_env/bin/activate && cd $BASE_DIR/vision_backend && python3 app.py; exec bash"
