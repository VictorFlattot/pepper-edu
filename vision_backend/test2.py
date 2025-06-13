# -*- coding: utf-8 -*-
import open3d as o3d
import numpy as np
import cv2
import os
import json
import math
from tqdm import tqdm

CAPTURE_DIR = "capture"
FX = FY = 200.0
DEPTH_SCALE = 1000.0
DEPTH_TRUNC = 3.0
VOXEL_SIZE = 0.01

with open(os.path.join(CAPTURE_DIR, "poses.json")) as f:
    poses = json.load(f)

pcd_all = o3d.geometry.PointCloud()

for key in tqdm(sorted(poses.keys())):
    rgb_path = os.path.join(CAPTURE_DIR, "rgb_%s.png" % key)
    depth_path = os.path.join(CAPTURE_DIR, "depth_%s.png" % key)

    rgb = cv2.imread(rgb_path)
    depth = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)

    rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
    rgb = cv2.resize(rgb, (depth.shape[1], depth.shape[0]))

    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        o3d.geometry.Image(rgb),
        o3d.geometry.Image(depth),
        depth_scale=DEPTH_SCALE,
        depth_trunc=DEPTH_TRUNC,
        convert_rgb_to_intensity=False
    )

    h, w = depth.shape
    cx, cy = w / 2.0, h / 2.0
    intrinsics = o3d.camera.PinholeCameraIntrinsic(w, h, FX, FY, cx, cy)

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsics)
    pcd.estimate_normals()

    x, y, theta = poses[key]
    T = np.eye(4)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    T[:3, :3] = [[cos_t, -sin_t, 0],
                 [sin_t,  cos_t, 0],
                 [0,      0,     1]]
    pcd.transform(T)

    pcd_all += pcd

pcd_all = pcd_all.voxel_down_sample(VOXEL_SIZE)
pcd_all.estimate_normals()

print("🧱 Reconstruction Poisson...")
mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd_all, depth=9)
mesh.compute_vertex_normals()

print("🧼 Nettoyage...")
mesh = mesh.remove_duplicated_vertices()
mesh = mesh.remove_degenerate_triangles()
mesh = mesh.remove_duplicated_triangles()
mesh = mesh.remove_non_manifold_edges()

o3d.io.write_triangle_mesh("mesh_reconstruit.ply", mesh)
o3d.visualization.draw_geometries([mesh])
