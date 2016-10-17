import numpy as np
import sys

from vispy import app, scene

from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from multi_iso_visual import MultiIsoVisual

hdu = fits.open('l1448_13co.fits')[0]
data = np.nan_to_num(hdu.data)
data /= 4

# Create a canvas with a 3D viewport
canvas = scene.SceneCanvas(keys='interactive', config={'depth_size': 24})
view = canvas.central_widget.add_view()

from scipy.ndimage import gaussian_filter

data = gaussian_filter(data, 1)


from vispy.color import BaseColormap
class TransGrays(BaseColormap):
    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t*0.6, t, t, t*0.05);
    }
    """


# Create isosurface visual
'''
    # threshold : float
        # The threshold to use for the isosurface render method. By default
        # the mean of the given volume is used.

    # clim : tuple of two floats | None
        # The contrast limits. The values in the volume are mapped to
        # black and white corresponding to these values.
'''
surface = MultiIsoVisual(data, parent=view.scene, threshold=0.8, step=3, cmap=TransGrays(),
                         relative_step_size=0.5, emulate_texture=True)
surface.step = 4
# surface.set_gl_state('translucent', cull_face=False)

# Add a 3D axis to keep us oriented
axis = scene.visuals.XYZAxis(parent=view.scene)

# Use a 3D camera
# Manual bounds; Mesh visual does not provide bounds yet
# Note how you can set bounds before assigning the camera to the viewbox
cam = scene.TurntableCamera(elevation=30, azimuth=30)
view.camera = cam

if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()