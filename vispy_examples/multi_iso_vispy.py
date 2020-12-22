# Example adapted from VisPy, which is released under the BSD license

# This script enables multiple isosurfaces based on the variable 'level' defined in glsl code.
# The color and transparency is cauculated according to 'level' and 'threshold'.
# TODO: improve colormap, current one is kind of random.
# TODO: make variable 'level' uniform or rewrite the visual class which could accetp 'level' as arguments.

import sys
import numpy as np

from vispy import app, scene
from vispy.gloo import gl
from astropy.io import fits
from vispy.visuals.volume import frag_dict, FRAG_SHADER

# Custom shader to replace existing iso one

ISO_SNIPPETS = dict(
    before_loop="""
        vec4 total_color = vec4(0.0);  // final color
        vec4 src = vec4(0.0);
        vec4 dst = vec4(0.0);
        vec3 dstep = 1.5 / u_shape;  // step to sample derivative
        gl_FragColor = vec4(0.0);
        float val_prev = 0;
        float outa = 0;
        vec3 loc_prev = vec3(0.0);
        vec3 loc_mid = vec3(0.0);
        
        int level = 4; // level is the number of isosurface layers
        
    """,
    in_loop="""
        for (int i=0; i<level; i++){

        // render from outside to inside
        if (val < u_threshold*(1.0-i/float(level)) && val_prev > u_threshold*(1.0-i/float(level))){
            // Use bisection to find correct position of contour
            for (int i=0; i<20; i++) {
                loc_mid = 0.5 * (loc_prev + loc);
                val = $sample(u_volumetex, loc_mid).g;
                if (val < u_threshold) {
                    loc = loc_mid;
                } else {
                    loc_prev = loc_mid;
                }
            }
            
            dst = $cmap(val);  // this will call colormap function if have
            dst = calculateColor(dst, loc, dstep);
            dst.a = 1. * (1.0 - i/float(level)); // transparency
            
            src = total_color;
            
            outa = src.a + dst.a * (1 - src.a);
            total_color = (src * src.a + dst * dst.a * (1 - src.a)) / outa;
            total_color.a = outa;
        }
        }
        val_prev = val;
        loc_prev = loc;
        """,
    after_loop="""
        gl_FragColor = total_color;
        """,
)

ISO_FRAG_SHADER = FRAG_SHADER.format(**ISO_SNIPPETS)

frag_dict['iso'] = ISO_FRAG_SHADER


hdu = fits.open('L1448_13CO.fits')[0]
data = np.nan_to_num(hdu.data)

# Create a canvas with a 3D viewport
canvas = scene.SceneCanvas(keys='interactive', config={'depth_size': 24})
view = canvas.central_widget.add_view()


from vispy.color import BaseColormap

# create colormaps that work well for translucent and additive volume rendering
# TODO: use a better color scheme to replace
class TransFire(BaseColormap):
    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
    }
    """

class TransGrays(BaseColormap):
    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t, t, t, t*0.05);
    }
    """

data /= 4


from scipy.ndimage import gaussian_filter

data = gaussian_filter(data, 1)

# Create isosurface visual
'''
    # threshold : float
        # The threshold to use for the isosurface render method. By default
        # the mean of the given volume is used.

    # clim : tuple of two floats | None
        # The contrast limits. The values in the volume are mapped to
        # black and white corresponding to these values.
'''
surface = scene.visuals.Volume(data, clim=(0, 1), method='iso',
                               parent=view.scene, cmap=TransGrays(),
                               relative_step_size=0.5, emulate_texture=True)
surface.shared_program['u_threshold'] = 0.8
# bind uniforms

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
