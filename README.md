# pepper-edu

Une plateforme pédagogique interactive utilisant le robot humanoïde Pepper pour accompagner des sessions d’éducation thérapeutique sur le risque cardiovasculaire.

1. [**Contexte et motivation**](#contexte-et-motivation) 
2. [**Installation**](#installation)  
3. [**Usage**](#usage)
3. [**Contact**](#contact)

## Contexte et motivation

Le projet **pepper-edu** s’appuie sur les livrets « Éducation et Prévention des Maladies Chroniques » (EPMC) conçus par Dr Xavier Debussche et Maryvette Balcou-Debussche. Ces livrets offrent un cadre didactique éprouvé pour faire prendre conscience aux apprenants des facteurs modifiables influençant le risque cardiovasculaire, en combinant supports écrits, manipulations, échanges de groupe et expérimentations.

En introduisant Pepper comme médiateur pédagogique (« outil interactif »), le formateur peut :
- guider individuellement la saisie des données biologiques (tension, cholestérol, glycémie…) via la tablette du robot ;  
- renforcer l’attention et l’engagement par des messages vocaux et visuels ;  
- centraliser en temps réel les résultats sur une interface web dédiée au formateur.

L’objectif est d’offrir une séance d’environ 2 heures où chaque participant :
1. Évalue son **Total Santé** (score de 0 à 60) en fonction de six variables.  
2. Comprend les mécanismes de la plaque d’athérome.  
3. Découvre et choisit deux actions concrètes (une alimentaire, une activité ou comportementale).  
4. Analyse la faisabilité de ces choix et s’engage à un plan d’action.

## Fonctionnalités principales

- **Recueil interactif de données**  
  Pepper pose successivement les 6 questions clés, affiche les barèmes et convertit les valeurs en points.

- **Calcul et restitution du Total Santé**  
  Le score est annoncé vocalement par Pepper et affiché sur l’interface formateur.

- **Affichage pédagogique**  
  - Illustration de l’évolution de la plaque d’athérome 
  - Présentation des 10 cartes d’actions

- **Interface web formateur**  
  Visualisation en temps réel des scores individuels et collectifs, suivi des choix, export CSV/PDF.

- **Architecture modulaire**  
  - **Backend** : Flask + NAOqi pour communiquer avec Pepper (API REST)  
  - **Frontend** : React pour le dashboard formateur  
  - **Blueprints** : route universelle pour l’affichage tablette, gestion des données et export

## Installation

### Préparation de l’environnement Python 2.7 isolé

Dans cette sous-section, nous allons créer un environnement Python 2.7 isolé afin de pouvoir installer et utiliser le SDK NAOqi sans interférer avec le système global. Cela garantit que les dépendances liées à Pepper restent confinées à cet environnement et n’impactent pas d’autres projets Python.

---

#### 1. Installer Python 2.7 et Virtualenv

```bash
sudo apt update
sudo apt install python2.7 python2.7-dev python-pip
sudo pip install --upgrade pip virtualenv
```

- **python2.7-dev** inclut les en-têtes pour compiler d’éventuelles extensions C.
- **virtualenv** permet de créer un environnement isolé pour Python, évitant les conflits de versions de paquets.

#### 2. Créer un environnement virtuel pour Python 2.7

```bash
mkdir -p ~/pepper_dev
cd ~/pepper_dev

virtualenv -p /usr/bin/python2.7 pepper_env
```

- Le flag **-p /usr/bin/python2.7** précise l’interpréteur à utiliser.
- Le dossier **pepper_env/** contiendra une installation propre de Python 2.7.

#### 3. Activer l’environnement virtuel

```bash
source pepper_env/bin/activate
```

- Vous devriez voir **(pepper_env)** en début de ligne.
- Tous les paquets installés via pip seront alors isolés dans **pepper_env/lib/....**

#### 4. Installer les dépendances du backend

```bash
cd backend
pip install -r requirements.txt
```

### Installation du SDK NAOqi

Avant de lancer votre backend Flask, installez la bibliothèque cliente NAOqi pour Python 2.7 en suivant ces étapes :

---

#### 1. Créer le répertoire du SDK et télécharger l’archive

```bash
mkdir -p ~/pepper_dev/naoqi-sdk
cd ~/pepper_dev/naoqi-sdk
wget https://community-static.aldebaran.com/resources/2.5.10/Python%20SDK/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz
```

#### 2. Décompresser l’archive

```bash
tar -xzf pynaoqi-python2.7-2.5.7.1-linux64.tar.gz
```

Le dossier obtenu est :

```bash
~/pepper_dev/naoqi-sdk/pynaoqi-python2.7-2.5.7.1-linux64/
```

#### 3. Ajouter NAOqi au PYTHONPATH de l’environnement virtuel

```bash
cd ~/pepper_dev
echo 'export PYTHONPATH=$PYTHONPATH:~/pepper_dev/naoqi-sdk/pynaoqi-python2.7-2.5.7.1-linux64/lib/python2.7/site-packages' \
  >> pepper_env/bin/activate
source pepper_env/bin/activate
```

Chaque activation de pepper_env ajoutera automatiquement les modules NAOqi.

#### 4. Installer les dépendances système

Certaines fonctionnalités (vidéo, audio, interface tablette) requièrent des libs C/C++ :

```bash
sudo apt update
sudo apt install \
  libjpeg-dev libpng-dev \
  libavcodec-dev libavformat-dev libswscale-dev \
  libqt4-opengl libqtgui4 libqtcore4
```

#### 5. Vérifier l’installation

Dans pepper_env, lancez :

```bash
python - <<'EOF'
try:
  import naoqi
  print("NAOqi SDK importé avec succès")
except Exception as e:
  print("Erreur lors de l'import du SDK :", e)
EOF

```

### Environnement Vision (Python 3)

Le service de vision utilise Flask, OpenCV et MediaPipe sous Python 3. Pour le configurer, procédez comme suit :

#### 1. Installer Python 3 et venv  
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

#### 2. Créer et activer l’environnement virtuel
```bash
cd ~/pepper_dev
python3 -m venv vision_env
source vision_env/bin/activate
```

#### 3. Installer les dépendances
```bash
pip install -r vision_backend/requirements.txt
```

#### 4. Installer les bibliothèques système pour OpenCV
```bash
sudo apt install libjpeg-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev
```

#### 5. Tester le service
```bash
cd vision_backend
python app.py
```
Puis, dans un autre terminal :
```bash
curl http://localhost:5050/ping
```
Vous devriez obtenir :
```json
{"success":true,"message":"Vision OK"}

```

## Usage

### 1. Activer les environnements virtuels

Ouvrez deux terminaux :

```bash
# Terminal 1 : pour le backend Pepper
source ~/pepper_dev/pepper_env/bin/activate
```
```bash
# Terminal 2 : pour le service Vision
source ~/pepper_dev/vision_env/bin/activate
```

### 2. Lancer le backend Flask (API Pepper)
Dans **Terminal 1** :
```bash
cd ~/pepper-edu/backend
python app.py
```
L’API Pepper est désormais disponible sur http://localhost:5000.

### 3. Lancer le service Vision (MediaPipe)
Dans **Terminal 2** :
```bash
cd ~/pepper-edu/vision_backend
python app.py
```
Le service Vision écoute sur http://localhost:5050.

### 4. Lancer le frontend React
Ouvrez un **Terminal 3** (ou un onglet) sans activer d’env virtuel :
```bash
cd ~/pepper-edu/frontend
npm install    # si ce n'est pas déjà fait
npm run dev    # ou `npm start` suivant votre config
```
L’interface dashboard est accessible sur http://localhost:5173.

### Lancement rapide avec `start_all.sh`

Plutôt que de démarrer manuellement chaque composant, vous pouvez utiliser le script fourni :

```bash
# Depuis la racine du dépôt
chmod +x start_all.sh
./start_all.sh
```
Ce script lance automatiquement :
- Backend Pepper (Flask) sur le port 5000
- Service Vision (Flask + MediaPipe) sur le port 5050
- Frontend React sur le port 3000

### Vérifier les connexions
```bash
curl http://localhost:5000/ping    # doit renvoyer {"success":true,"message":"Backend OK"}
curl http://localhost:5050/ping    # doit renvoyer {"success":true,"message":"Vision OK"}
```
Ouvrez ensuite votre navigateur sur http://localhost:5173 pour accéder au dashboard

## Contact

Pour toute question, suggestion ou rapport de bug, n’hésitez pas à me contacter :

- **GitHub Issues** : Ouvrez une issue sur le dépôt  
  https://github.com/VictorFlattot/pepper-edu/issues  
- **Email** : victor.flattot@gmail.com  

Merci !  