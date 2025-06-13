# -*- coding: utf-8 -*-
import numpy as np
import cv2, heapq
from naoqi import ALProxy

def get_slam_map(ip, port, map_name):
    nav = ALProxy("ALNavigation", ip, port)
    nav.stopLocalization()
    nav.stopExploration()
    nav.loadExploration(map_name)
    res, w, h, _, data = nav.getMetricalMap()
    raw = np.array(data).reshape((w, h))
    return raw.T, res

def get_pepper_position_in_map(ip, port):
    nav = ALProxy("ALNavigation", ip, port)
    nav.startLocalization()
    try:
        result = nav.getRobotPositionInMap()
        print("🔎 Résultat brut :", result)

        if isinstance(result, list) and len(result) >= 1 and isinstance(result[0], list) and len(result[0]) == 3:
            x, y, theta = result[0]
            print("✅ Localisation réussie")
            print("X : %.3f m" % x)
            print("Y : %.3f m" % y)
            print("Theta : %.3f rad (%.1f°)" % (theta, theta * 180.0 / 3.14159))
            return x, y, theta
        else:
            raise ValueError("Format inattendu : %s" % str(result))

    except Exception as e:
        print("❌ Échec de localisation :", e)
        return None

def cm_to_pixels(cm, resolution):
    return int(round((cm / 100.0) / resolution))

def make_binary_map(raw_map):
    return np.where(raw_map == 0, 0, 1).astype(np.uint8)

def apply_closing(binary_map, closing_px):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * closing_px + 1, 2 * closing_px + 1))
    return cv2.morphologyEx(binary_map, cv2.MORPH_CLOSE, kernel)

def apply_dilation(closed_map, dilate_px):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * dilate_px + 1, 2 * dilate_px + 1))
    return cv2.dilate(closed_map, kernel)

def crop_to_content(mask, margin=10):
    free_y, free_x = np.where(mask == 0)
    if len(free_x) == 0 or len(free_y) == 0:
        return mask, (0, 0)
    x_min = max(np.min(free_x) - margin, 0)
    x_max = min(np.max(free_x) + margin, mask.shape[1])
    y_min = max(np.min(free_y) - margin, 0)
    y_max = min(np.max(free_y) + margin, mask.shape[0])
    return mask[y_min:y_max, x_min:x_max], (x_min, y_min)

def astar(grid, start, goal):
    h, w = grid.shape
    open_set = [(0 + heuristic(start, goal), 0, start)]
    came_from = {}
    g_score = {start: 0}
    visited = set()
    directions = [(-1,0),(1,0),(0,-1),(0,1), (-1,-1),(-1,1),(1,-1),(1,1)]
    while open_set:
        _, cost, current = heapq.heappop(open_set)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        visited.add(current)
        for dy, dx in directions:
            ny, nx = current[0]+dy, current[1]+dx
            neighbor = (ny, nx)
            if 0 <= ny < h and 0 <= nx < w:
                if grid[ny][nx] == 0 and neighbor not in visited:
                    move_cost = 1.4 if abs(dy) + abs(dx) == 2 else 1
                    new_cost = cost + move_cost
                    if neighbor not in g_score or new_cost < g_score[neighbor]:
                        g_score[neighbor] = new_cost
                        heapq.heappush(open_set, (new_cost + heuristic(neighbor, goal), new_cost, neighbor))
                        came_from[neighbor] = current
    return None

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def draw_interactive_astar_map(cropped, path, start, goal, scale=4, pepper_pos=None, resolution=0.05, offset=(0,0)):
    h, w = cropped.shape
    overlay = np.zeros((h, w, 3), dtype=np.uint8)
    overlay[cropped == 1] = [0, 0, 0]
    overlay[cropped == 0] = [255, 255, 255]
    for (y, x) in path:
        overlay[y, x] = [255, 0, 0]
    overlay[start[0], start[1]] = [0, 255, 0]
    overlay[goal[0], goal[1]] = [0, 0, 255]

    if pepper_pos:
        x_m, y_m = pepper_pos[0], pepper_pos[1]
        px = int(round(x_m / resolution)) - offset[0]
        py = int(round(y_m / resolution)) - offset[1]
        print("📍 Position de Pepper dans la carte croppée : (%d, %d) (px)" % (py, px))
        if 0 <= py < h and 0 <= px < w:
            overlay[py, px] = [0, 255, 255]  # cyan = Pepper

    zoomed = cv2.resize(overlay, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)
    cv2.imshow("Chemin interactif A*", zoomed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    pepper_ip = "11.255.255.100"
    map_name = "2025-05-23T073304.052Z"

    raw_map, resolution = get_slam_map(pepper_ip, 9559, map_name)
    closing_px = 10
    dilate_px = cm_to_pixels(20, resolution)

    binary_map = make_binary_map(raw_map)
    closed_map = apply_closing(binary_map, closing_px)
    inflated_map = apply_dilation(closed_map, dilate_px)

    cropped, offset = crop_to_content(inflated_map, margin=10)
    h, w = cropped.shape
    scale = 4
    zoomed = cv2.resize(((1 - cropped) * 255).astype(np.uint8), (w*scale, h*scale), interpolation=cv2.INTER_NEAREST)
    zoomed_color = cv2.cvtColor(zoomed, cv2.COLOR_GRAY2BGR)

    click_points = []

    # def mouse_callback(event, x, y, flags, param):
    #     if event == cv2.EVENT_LBUTTONDOWN:
    #         gx, gy = x // scale, y // scale
    #         click_points.append((gy, gx))
    #         print("🖱️ Point cliqué : (%d, %d)" % (gy, gx))

    # cv2.imshow("Cliquez Start puis Goal", zoomed_color)
    # cv2.setMouseCallback("Cliquez Start puis Goal", mouse_callback)

    # while len(click_points) < 2:
    #     cv2.waitKey(1)

    # cv2.destroyAllWindows()

    # start, goal = click_points[0], click_points[1]
    # print("🚀 Calcul du chemin de %s -> %s" % (str(start), str(goal)))
    # path = astar(cropped, start, goal)

    # if path:
    #     print("📡 Tentative de récupération de la position réelle de Pepper :")
    #     pepper_pose = get_pepper_position_in_map(pepper_ip, 9559)
    #     draw_interactive_astar_map(cropped, path, start, goal, scale=4, pepper_pos=pepper_pose, resolution=resolution, offset=offset)
    # else:
    #     print("❌ Aucun chemin trouvé.")
