# pepper-edu

Une plateforme pédagogique interactive utilisant le robot humanoïde Pepper pour accompagner des sessions d’éducation thérapeutique sur le risque cardiovasculaire.

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
  - Illustration de l’évolution de la plaque d’athérome (phase 1.6)  
  - Présentation des 10 cartes d’actions (phases 2.1–2.3)  
  - Rapide infographie chronologique des étapes (Timeline)

- **Interface web formateur**  
  Visualisation en temps réel des scores individuels et collectifs, suivi des choix, export CSV/PDF.

- **Architecture modulaire**  
  - **Backend** : Flask + NAOqi pour communiquer avec Pepper (API REST)  
  - **Frontend** : React pour le dashboard formateur  
  - **Blueprints** : route universelle pour l’affichage tablette, gestion des données et export

## Installation

### Prérequis

- Python 2.7 (compatible avec NAOqi)  
- ROS Kinetic (pour l’intégration du driver Pepper)  
- Node.js + npm (frontend React)

### Backend

```bash
cd backend
pip install -r requirements.txt
# configurer l’IP de Pepper dans config.py ou via la variable d’environnement PEPPER_IP
python app.py
