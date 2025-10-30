import matplotlib
matplotlib.use('QtAgg')
from matplotlib import pyplot as plt
import matplotlib.path as mpath

import numpy as np
import cartopy.crs as ccrs

def draw_map(extent):
    # pulled from draw_map_gui.py
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.SouthPolarStereo(central_longitude=180)})
    ax.set_extent([-180, 180, -90, extent], crs=ccrs.PlateCarree())

    parallels = np.arange(-90, 120, 10)
    meridians = np.arange(-420, 420, 60)

    gl = ax.gridlines(xlocs=meridians, ylocs=[], draw_labels=True, rotate_labels=False,
        linestyle='--', color='gray')
    ax.gridlines(xlocs=[], ylocs=parallels, draw_labels=True, 
        linestyle='--', color='gray')

    gl.top_labels

    # clip path to make stereo projection circular:
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)

    ax.set_boundary(circle, transform=ax.transAxes)

    plt.show()

# draw_map(-40)
