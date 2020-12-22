__author__ = 'Penny Qian'
"""
This script is to test creating IsoSurface based on Gaussian Density Estimation for scatter points
Some displacement exists between the scatter points and the produced IsoSurface
"""

import numpy as np
from vispy import app, scene, io
from vispy.color import Color
from scipy import stats


# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True, bgcolor='white')
canvas.measure_fps()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create three cameras (Fly, Turntable and Arcball)
fov = 60.
cam2 = scene.cameras.TurntableCamera(parent=view.scene, fov=fov,
                                     name='Turntable')
view.camera = cam2  # Select turntable at first

# Add scatter plots here
n = 5000
pos = np.random.normal(size=(n, 3), scale=0.2)

# one could stop here for the data generation, the rest is just to make the
# data look more interesting. Copied over from magnify.py

centers = np.random.normal(size=(50, 3))
indexes = np.random.normal(size=n, loc=centers.shape[0] / 2.,
                           scale=centers.shape[0] / 3.)
indexes = np.clip(indexes, 0, centers.shape[0] - 1).astype(int)
scales = 10 ** (np.linspace(-2, 0.5, centers.shape[0]))[indexes][:, np.newaxis]
pos *= scales
pos += centers[indexes]

xmin, ymin, zmin = pos.min(axis=0)
xmax, ymax, zmax = pos.max(axis=0)
s = [zmax - zmin, ymax - ymin, xmax - xmin]
X, Y, Z = pos[:, 0], pos[:, 1], pos[:, 2]

scatter_color = np.ones((n, 4), dtype=np.float32)
for idx in range(n):
    scatter_color[idx] = Color('green').rgba
scatter = scene.visuals.Markers()
scatter.set_data(pos, face_color=scatter_color, scaling=False, symbol='disc', size=2)

print('centers averate', centers[:, 0].shape, np.average(centers[:, 0], axis=0), np.average(centers[:, 1], axis=0),
      np.average(centers[:, 2], axis=0))
scat_trans = [-np.average(centers[:, 0], axis=0), -np.average(centers[:, 1], axis=0),
              -np.average(centers[:, 2], axis=0)]
scatter.transform = scene.STTransform(translate=scat_trans)
view.add(scatter)

# ------------- Gaussian Density estimation---------------
values = pos.T
# 2-D array with shape (# of dims, # of data).
kde = stats.gaussian_kde(values)

# Create a regular 3D grid with 50 points in each dimension
xi, yi, zi = np.mgrid[xmin:xmax:50j, ymin:ymax:50j, zmin:zmax:50j]  # which means from xmin to xmax it's divided by 50

# Evaluate the KDE on a regular grid...
coords = np.vstack([item.ravel() for item in [xi, yi, zi]])
density = kde(coords).reshape(xi.shape)

# ---------------------------------------------------------

# The scale of the isosurface should be modified by combining the dataset scale and grid segments
sur_scale = [(xmax - xmin) / 50., (ymax - ymin) / 50., (zmax - zmin) / 50.]
trans = (-s[2] / 2.0, -s[1] / 2.0, -s[0] / 2.0)

surface = scene.visuals.Isosurface(density, level=density.max() / 2., shading=None,
                                   color=(1, 0.6, 1, 0.5),
                                   parent=view.scene)
surface.set_gl_state(depth_test=True, cull_face=True)
surface.transform = scene.STTransform(translate=trans, scale=sur_scale)

surface2 = scene.visuals.Isosurface(density, level=density.max() / 5., shading=None,
                                    color=(0, 0.6, 0, 0.3),
                                    parent=view.scene)
surface2.set_gl_state(depth_test=True, cull_face=True)
surface2.transform = scene.STTransform(translate=trans, scale=sur_scale)

# Add a 3D axis to keep us oriented
axis = scene.visuals.XYZAxis(parent=view.scene)

if __name__ == '__main__':
    print(__doc__)
    app.run()
