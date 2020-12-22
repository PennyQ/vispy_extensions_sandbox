__author__ = 'penny'
'''
Use gaussian density kernel estimation to smooth catalogue points into 
a continuous function, and apply it as the input for isosurface.
'''
import sys
import numpy as np
from scipy import stats
from mayavi import mlab
import pyfits
from vispy import app, scene

fitsfile = pyfits.open('cloud_catalog_july14_2015.fits')

n = len(fitsfile[1].data['x_gal'])
P = np.zeros((n,3), dtype=np.float32)

X, Y, Z = P[:,0],P[:,1],P[:,2]
X[...] = fitsfile[1].data['x_gal']
Y[...] = fitsfile[1].data['y_gal']
Z[...] = fitsfile[1].data['z_gal']
P = np.nan_to_num(P)
print(P.shape)

# mu=np.array([1,10,20])
# Let's change this so that the points won't all lie in a plane...
# sigma=np.matrix([[20,10,10],
#                  [10,25,1],
#                  [10,1,50]])

# data=np.random.multivariate_normal(mu,sigma,1000)
data = P
values = data.T
print('data', data, data.shape)

# 2-D array with shape (# of dims, # of data).
kde = stats.gaussian_kde(values)

# Create a regular 3D grid with 50 points in each dimension
xmin, ymin, zmin = data.min(axis=0)
xmax, ymax, zmax = data.max(axis=0)
xi, yi, zi = np.mgrid[xmin:xmax:50j, ymin:ymax:50j, zmin:zmax:50j] # which means from xmin to xmax it's divided by 50
print('xi yi zi', xi, xi.shape) # the shape is (50, 50, 50)

# Evaluate the KDE on a regular grid...
coords = np.vstack([item.ravel() for item in [xi, yi, zi]])
# numpy.ravel Return a contiguous flattened array.
# numpy.vstack Stack arrays in sequence vertically (row wise).

density = kde(coords).reshape(xi.shape)
print(density, density.shape)


def get_min_and_max(array):
    return float("%.4g" % np.nanmin(array)), float("%.4g" % np.nanmax(array))
#-----------
# For volume data, it's kind of already 'gridded'

trans = (-(xmax-xmin)/2.0, -(ymax-ymin)/2.0, -(zmax-zmin)/2.0)

# Create a canvas with a 3D viewport
canvas = scene.SceneCanvas(keys='interactive', config={'depth_size': 24}, bgcolor='white')
view = canvas.central_widget.add_view()

surface = scene.visuals.Isosurface(density, level=density.max()/2., shading=None,
                                   color=(0.5, 0.6, 1, 0.5),
                                   parent=view.scene)
# surface.transform = scene.transforms.STTransform(translate=(-len(X)/2., -len(Y)/2., -len(Z)/2.))
surface.set_gl_state(depth_test=True, cull_face=True)
surface.transform = scene.STTransform(translate=trans)

surface2 = scene.visuals.Isosurface(density, level=density.max()/4., shading=None,
                                    color=(1, 0, 0, 0.1),
                                    parent=view.scene)
# surface2.transform = scene.transforms.STTransform(translate=(-s[0]/2., -s[1]/2., -s[2]/2.))
surface2.set_gl_state(depth_test=True, cull_face=True)
surface2.transform = scene.STTransform(translate=trans)




# Add a 3D scatter plot
scat_visual = scene.visuals.Markers()
scat_visual.set_data(P, symbol='disc', edge_color=None, face_color='red', size=5)

scat_visual.transform = scene.STTransform(translate=trans)

view.add(scat_visual)

# Add a 3D axis to keep us oriented
axis = scene.visuals.XYZAxis(parent=view.scene)

# Use a 3D camera
# Manual bounds; Mesh visual does not provide bounds yet
# Note how you can set bounds before assigning the camera to the viewbox
cam = scene.TurntableCamera(elevation=30, azimuth=30)
cam.set_range((-10, 10), (-10, 10), (-10, 10))

view.camera = cam

# Visualize the density estimate as isosurfaces
# mlab.contour3d(xi, yi, zi, density, opacity=0.5)
# mlab.axes()
# mlab.show()

if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()