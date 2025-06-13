# -*- coding: utf-8 -*-
from naoqi import ALProxy
import numpy as np
import cv2
import os
import time
import math

PEPPER_IP = "11.255.255.100"
PEPPER_PORT = 9559
NB_CAPTURES = 30
RADIUS = 0.1  # en mètres (juste pour info)
THETA_STEP = 2 * math.pi / NB_CAPTURES
DELAY = 1.5
SAVE_DIR = "orbital_captures"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

motion = ALProxy("ALMotion", PEPPER_IP, PEPPER_PORT)
video = ALProxy("ALVideoDevice", PEPPER_IP, PEPPER_PORT)

# Caméras
res = 1
color_sub = video.subscribeCamera("color_cam", 0, res, 11, 30)
depth_sub = video.subscribeCamera("depth_cam", 2, res, 17, 30)

def get_rgb_depth():
    rgb_data = video.getImageRemote(color_sub)
    depth_data = video.getImageRemote(depth_sub)
    rgb = np.frombuffer(rgb_data[6], dtype=np.uint8).reshape((rgb_data[1], rgb_data[0], 3))
    depth = np.frombuffer(depth_data[6], dtype=np.uint16).reshape((depth_data[1], depth_data[0]))
    return rgb, depth

print("🔁 Début de la rotation orbitale à rayon %.2fm..." % RADIUS)

for i in range(NB_CAPTURES):
    print("📸 Capture %d/%d" % (i+1, NB_CAPTURES))

    rgb, depth = get_rgb_depth()
    cv2.imwrite(os.path.join(SAVE_DIR, "rgb_%03d.png" % i), rgb)
    cv2.imwrite(os.path.join(SAVE_DIR, "depth_%03d.png" % i), depth)

    if i < NB_CAPTURES - 1:
        arc_len = RADIUS * THETA_STEP
        motion.moveTo(arc_len, 0.0, THETA_STEP)
        time.sleep(DELAY)

video.unsubscribe(color_sub)
video.unsubscribe(depth_sub)

print("✅ Captures terminées dans : %s" % SAVE_DIR)
