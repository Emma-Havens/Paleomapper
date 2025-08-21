
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
import numpy as np

from enum import Enum
from matplotlib.colors import ListedColormap, Normalize, BoundaryNorm

class ColorbarType(Enum):
    OCEAN_BAR = 1,
    GEO_BAR = 2,
    PLATE_BAR = 3

quaternary = (249, 249, 127)
neogene = (255, 230, 25)
paleogene = (253, 154, 82)
cretaceous = (127, 198, 78)
jurassic = (52, 178, 201)
triassic = (129, 43, 146)
permian = (240, 64, 40)
carboniferous = (103, 165, 153)
devonian = (203, 140, 55)
silurian = (179, 225, 182)
ordovician = (0, 146, 112)
cambrian = (127, 160, 86)

ediacaran = (254, 217, 106)
cryogenian = (254, 204, 92)
tonian = (254, 191, 78)
stenian = (254, 217, 154)
ectasian = (253, 204, 138)
calymmian = (253, 192, 122)
statherian = (248, 117, 167)
orosirian = (247, 104, 152)
rhyacian = (247, 91, 137)
siderian = (247, 79, 124)
neoarchean = (249, 155, 193)
mesoarchean = (247, 104, 169)
paleoarchean = (244, 68, 159)
eoarchean = (218, 3, 127)
hadean = (174, 2, 126)

cenozoic = (242, 249, 29)
mesozoic = (103, 197, 202)
paleozoic = (153, 192, 141)

proterozoic = (247, 53, 99)
archean = (240, 4, 127)
precambrian = (247, 67, 112)

# from mpl
def plot_examples(colormaps):
    """
    Helper function to plot data with associated colormap.
    """
    np.random.seed(19680801)
    data = np.random.randint(0, 539, (30, 30))
    n = len(colormaps)
    fig, axs = plt.subplots(1, n, figsize=(n * 2 + 2, 3),
                            layout='constrained', squeeze=False)
    for [ax, cmap] in zip(axs.flat, colormaps):
        psm = ax.pcolormesh(data, cmap=cmap, rasterized=True, vmin=0, vmax=539)
        fig.colorbar(psm, ax=ax)
    plt.show()

def plot_colorbars(colormaps, bounds, label_masks, yaxis_names):
    n = len(colormaps)
    fig, axs = plt.subplots(n, 1, figsize=(30, n * 2),
                            layout='constrained', squeeze=False)
    
    for [ax, cmap, bound, mask, name] in zip(axs.flat, colormaps, bounds, label_masks, yaxis_names):
        # norm = Normalize(vmin=0, vmax=4567)
        # print(bound)
        norm = BoundaryNorm(bound, cmap.N)

        cb = fig.colorbar(mplcm.ScalarMappable(norm=norm, cmap=cmap),
                cax=ax, orientation='horizontal', extend='neither', spacing='proportional')

        cb.set_ticks(bound)
        ticklabels = [str(x) if mask[i] else "" for i, x in enumerate(bound)]
        cb.set_ticklabels(ticklabels)
        ax.set_ylabel(name)

    axs[-1, 0].set_xlabel('Time (Ma)')

    plt.show()

def zip_time_and_color(color_list, time_list):
    cmap_list = np.ones([time_list[-1], 4])
    for i in range(len(color_list)):
        start_time = time_list[i]
        end_time = time_list[i+1]
        color = color_list[i]

        cmap_list[start_time:end_time, :3] = color

    return cmap_list

rgb_norm = Normalize(0, 255)

# colors for colormaps defined in RGB scale 0-255
smallest_division_colors_unnorm = [quaternary, neogene, paleogene, cretaceous, jurassic, triassic, permian,
        carboniferous, devonian, silurian, ordovician, cambrian, ediacaran, cryogenian, tonian, stenian, 
        ectasian, calymmian, statherian, orosirian, rhyacian, siderian, neoarchean, mesoarchean, paleoarchean, 
        eoarchean, hadean]
phan_focused_unnorm = [quaternary, neogene, paleogene, cretaceous, jurassic, triassic, permian, carboniferous,
        devonian, silurian, ordovician, cambrian, proterozoic, archean, hadean ]
big_picture_unnorm = [ cenozoic, mesozoic, paleozoic, proterozoic, archean, hadean ]

# colors for colormaps defined in RGB scale 0-1 (necessary for mpl)
smallest_division_colors = [ rgb_norm(color) for color in smallest_division_colors_unnorm ]
phan_focused_colors = [ rgb_norm(color) for color in phan_focused_unnorm ]
big_picture_colors = [ rgb_norm(color) for color in big_picture_unnorm ]

# intervals for colors for each colormap
smallest_division_time = [ 0, 2, 23, 66, 143, 201, 252, 299, 359, 420, 443, 487, 539, 635, 720, 1000, 1200, 
        1400, 1600, 1800, 2050, 2300, 2500, 2800, 3200, 3600, 4031, 4567 ]
phan_focused_time = [ 0, 2, 23, 66, 143, 201, 252, 299, 359, 420, 443, 487, 539, 2500, 4031, 4567 ]
big_picture_time = [ 0, 66, 252, 539, 2500, 4031, 4567 ]

# colormaps to be used for colorbars
smallest_division = ListedColormap(smallest_division_colors)
phan_focused = ListedColormap(phan_focused_colors)
big_picture = ListedColormap(big_picture_colors)
phanerozoic = ListedColormap(smallest_division_colors[:12])

# label masks for colorbar plotting
smallest_division_mask = [ 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, # phanerozoic labels
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]
phan_focused_mask = [ 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1 ]
big_picture_mask = [ 1, 1, 1, 1, 1, 1, 1 ]
phanerozoic_mask = [ 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]

# plot colorbars
# plot_colorbars([smallest_division, phan_focused, big_picture, phanerozoic], 
#                [smallest_division_time, phan_focused_time, big_picture_time, smallest_division_time[:13]], 
#                [smallest_division_mask, phan_focused_mask, big_picture_mask, phanerozoic_mask],
#                ["Smallest Division", "Phan Focused", "Big Picture", "Phanerozoic"])

# bounds for colormaps used in draw_map_gui
smallest_division_norm = BoundaryNorm(smallest_division_time, smallest_division.N)

# geo_age_array = zip_time_and_color(smallest_division_colors, smallest_division_time)
