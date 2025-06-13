#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import cv2.aruco as aruco
import numpy as np
from naoqi import ALProxy
import time

# ← Remplacez par l’IP de votre Pepper
PEPPER_IP   = "11.255.255.100"
PEPPER_PORT = 9559

# Proxies
video   = ALProxy("ALVideoDevice",      PEPPER_IP, PEPPER_PORT)
motion  = ALProxy("ALMotion",           PEPPER_IP, PEPPER_PORT)
tts     = ALProxy("ALTextToSpeech",     PEPPER_IP, PEPPER_PORT)

# Paramètres ArUco
aruco_dict      = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters      = aruco.DetectorParameters_create()
marker_length   = 0.1    # taille du marqueur en m (100 mm)
axis_length     = 0.05   # longueur des axes à dessiner (m)

# Option calibration caméra (npz généré via cv2.calibrateCamera)
# calib = np.load("calib_cam.npz")
# camera_matrix, dist_coeffs = calib["mtx"], calib["dist"]
camera_matrix, dist_coeffs = None, None

def subscribe_camera():
    # cameraIndex=1 (caméra frontale), resolution=1 (VGA 640x480), colorSpace=11 (BGR), fps=30
    return video.subscribeCamera("aruco_stream", 0, 1, 11, 30)

def unsubscribe_camera(sub_id):
    video.unsubscribe(sub_id)

def get_frame(sub_id):
    # Renvoie un tableau numpy BGR 3-channels
    img = video.getImageRemote(sub_id)
    if img is None:
        return None
    width, height = img[0], img[1]
    array = np.frombuffer(img[6], dtype=np.uint8).reshape((height, width, 3))
    return array

def main():
    # Réveille Pepper et rigidifie la tête pour éviter qu’il ne bouge
    motion.wakeUp()
    motion.setStiffnesses("Head", 1.0)
    motion.setAngles(["HeadYaw","HeadPitch"], [0.0, 0.0], 0.1)

    sub_id = subscribe_camera()
    print("Flux vidéo démarré, Ctrl-C pour quitter")

    try:
        while True:
            frame = get_frame(sub_id)
            if frame is None:
                print("— pas d’image reçue, réabonnement…")
                unsubscribe_camera(sub_id)
                time.sleep(0.5)
                sub_id = subscribe_camera()
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            if ids is not None and len(ids)>0:
                aruco.drawDetectedMarkers(frame, corners, ids)
                print("Marqueurs détectés :", ids.flatten())

                if camera_matrix is not None:
                    rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(
                        corners,
                        marker_length,
                        camera_matrix,
                        dist_coeffs
                    )
                    for r, t in zip(rvecs, tvecs):
                        aruco.drawAxis(frame, camera_matrix, dist_coeffs, r, t, axis_length)

            cv2.imshow("Pepper ArUco", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # Échap pour quitter
                break

    except KeyboardInterrupt:
        pass
    finally:
        unsubscribe_camera(sub_id)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
