# The color scheme file is from ColorBrewer https://github.com/axismaps/colorbrewer/

import numpy as np
import sys
import pandas as pd

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


def get_color():
    import pandas as pd
    xl = pd.ExcelFile('ColorBrewer_all_schemes_RGBonly3.XLS')
    df = xl.parse('Sheet1')[:1690]

    # TODO: 4.0 here will be replaced by level, 'Blues' will be replaced by chosen color in dropdown list
    # select specific data series
    mask = df['ColorName'].isin(['Blues']) & df['NumOfColors'].isin([4]) & df['Type'].isin(['seq'])
    sel = df[mask]
    index = sel.index[0] # int
    df_rgb = df.loc[range(index, index+int(4.0), 1)]

    # get color array
    color = np.ones((int(4.0), 4))
    color[:, 0] = np.array(df_rgb['R'])
    color[:, 1] = np.array(df_rgb['G'])
    color[:, 2] = np.array(df_rgb['B'])
    color[:, 3] = 255.0
    color /= 255.
    global COLOR_BREWER
    COLOR_BREWER = color.tolist()
    # return color.tolist()

get_color()


class Brewer(BaseColormap):
    colors = COLOR_BREWER

    # Use $color_0 to refer to the first color in `colors`, and so on. These are vec4 vectors.
    glsl_map = """
    vec4 translucent_grays(int l) {
        if (l == 1)
            {return $color_0;}
        if (l == 2)
            {return $color_1;}
        if (l == 3)
            {return $color_2;}
        if (l == 4)
            {return $color_3;}

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
surface = MultiIsoVisual(data, parent=view.scene, threshold=0.8, step=2,
                         relative_step_size=0.5, emulate_texture=True)
# surface.step = 3
surface.cmap=Brewer()
# get color depends on step


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