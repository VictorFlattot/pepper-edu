# pepper/head_movement.py

import threading
import time

_bob_thread = None
_bobbing = False

def start_head_bobbing(session):
    global _bob_thread, _bobbing

    if _bobbing:
        return

    _bobbing = True
    motion = session.service("ALMotion")

    def bobbing_loop():
        while _bobbing:
            try:
                motion.setAngles("HeadPitch", 0.1, 0.15)
                time.sleep(0.5)
                motion.setAngles("HeadPitch", -0.1, 0.15)
                time.sleep(0.5)
            except Exception as e:
                print("Erreur head bobbing:", e)
                break

    _bob_thread = threading.Thread(target=bobbing_loop)
    _bob_thread.daemon = True
    _bob_thread.start()


def stop_head_bobbing():
    global _bobbing
    _bobbing = False
