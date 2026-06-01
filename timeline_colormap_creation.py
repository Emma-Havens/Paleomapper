
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
import numpy as np

from enum import Enum
from matplotlib.colors import ListedColormap, Normalize, BoundaryNorm

class ColorbarType(Enum):
    OCEAN_BAR = 1,
    GEO_BAR = 2,
    PLATE_BAR = 3

# holocene_stage = (254, 242, 236)
# upper_pleistocene = (255, 242, 211)
# middle_pleistocene = (255, 242, 199)
# calabrian = (255, 242, 186)
# gelasian = (255, 242, 174)
# piacenzian = (255, 255, 191)
# zanclean = (255, 255, 179)
# messinian = (255, 255, 115)
# tortonian = (255, 255, 102)
# serravallian = (255, 255, 89)
# langhian = (255, 255, 77)
# burdigalian = (255, 255, 65)
# aquitanian = (255, 255, 51)
# chattian = (254, 230, 170)
# rupelian = (254, 217, 154)
# priabonian = (253, 205, 161)
# bartonian = (253, 192, 145)
# lutetian = (252, 180, 130)
# ypresian = (252, 167, 115)
# thanetian = (253, 191, 111)
# selandian = (254, 191, 101)
# danian = (253, 180, 98)
# maastrichtian = (242, 250, 140)
# campanian = (230, 244, 127)
# santonian = (217, 239, 116)
# coniacian = (204, 233, 104)
# turonian = (191, 227, 93)
# cenomanian = (179, 222, 83)
# albian = (204, 234, 151)
# aptian = (191, 228, 138)
# barremian = (179, 223, 127)
# hauterivian = (166, 217, 117)
# valanginian = (153, 211, 106)
# barriasian = (140, 205, 96)
# tithonian = (217, 241, 247)
# kimmeridgian = (204, 236, 244)
# oxfordian = (191, 231, 241)
# callovian = (191, 231, 229)
# bathonian = (179, 226, 227)
# bajocian = (166, 221, 224)
# aalenian = (154, 217, 221)
# toarcian = (153, 206, 227)
# pliensbachian = (128, 197, 221)
# sinemurian = (103, 188, 216)
# hettangian = (78, 179, 211)
# rhaetian = (227, 185, 219)
# norian = (214, 170, 211)
# carnian = (201, 131, 191)
# ladinian = (201, 131, 191)
# anisian = (188, 117, 183)
# olenekian = (176, 81, 165)
# induan = (164, 70, 159)
# changhsingian = (252, 192, 178)
# wuchiapingian = (252, 180, 162)
# capitanian = (251, 154, 133)
# wordian = (251, 141, 118)
# roadian = (251, 128, 105)
# kungurian = (227, 135, 118)
# artinskian = (227, 123, 104)
# sakmarian = (227, 111, 92)
# asselian = (227, 99, 80)
# gzhelian = (204, 212, 199)
# kasimovian = (191, 208, 197)
# moscovian = (179, 203, 185)
# bashkirian = (153, 194, 181)
# serpukhovian = (191, 194, 107)
# visean = (166, 185, 108)
# tournaisian = (140, 176, 108)
# famennian = (242, 237, 197)
# frasnian = (242, 237, 197)
# givetian = (241, 225, 133)
# eifelian = (241, 213, 118)
# emsian = (229, 208, 117)
# pragian = (229, 208, 117)
# lochkovian = (229, 183, 90)
# pridoli_stage = (230, 245, 225)
# ludfordian = (217, 240, 223)
# gorstian = (204, 236, 221)
# homerian = (204, 235, 209)
# sheinwoodian = (191, 230, 195)
# telychian = (191, 230, 207)
# aeronian = (179, 225, 194)
# rhuddanian = (166, 220, 181)
# hirnantian = (166, 219, 171)
# katian = (153, 214, 159)
# sandbian = (140, 208, 148)
# darriwilian = (116, 198, 156)
# dapingian = (102, 192, 146)
# floian = (65, 176, 135)
# tremadocian = (51, 169, 126)
# stage_10 = (230, 245, 201)
# jiangshanian = (217, 240, 187)
# paibian = (204, 235, 174)
# guzhangian = (204, 233, 170)
# drumian = (191, 217, 157)
# stage_5 = (179, 212, 146)
# stage_4 = (179, 202, 142)
# stage_3 = (166, 197, 131)
# stage_2 = (166, 186, 128)
# fortunian = (153, 181, 117)

holocene = (254, 235, 210)
pleistocene = (255, 239, 175)
pliocene = (255, 255, 153)
miocene = (255, 255, 0)
oligocene = (253, 192, 122)
eocene = (253, 180, 108)
paleocene = (253, 167, 95)

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
smallest_division_colors_unnorm = [holocene, pleistocene, pliocene, miocene, oligocene, eocene, paleocene, 
        cretaceous, jurassic, triassic, permian, carboniferous, devonian, silurian, ordovician, cambrian, 
        ediacaran, cryogenian, tonian, stenian, ectasian, calymmian, statherian, orosirian, rhyacian, siderian, 
        neoarchean, mesoarchean, paleoarchean, eoarchean, hadean]
phan_focused_unnorm = [quaternary, neogene, paleogene, cretaceous, jurassic, triassic, permian, carboniferous,
        devonian, silurian, ordovician, cambrian, proterozoic, archean, hadean ]
big_picture_unnorm = [ cenozoic, mesozoic, paleozoic, proterozoic, archean, hadean ]

# colors for colormaps defined in RGB scale 0-1 (necessary for mpl)
smallest_division_colors = [ rgb_norm(color) for color in smallest_division_colors_unnorm ]
phan_focused_colors = [ rgb_norm(color) for color in phan_focused_unnorm ]
big_picture_colors = [ rgb_norm(color) for color in big_picture_unnorm ]

# intervals for colors for each colormap
smallest_division_time = [ 0, 0.0117, 2.58, 5.33, 23, 34, 56, 66, 143, 201, 252, 299, 359, 420, 443, 487, 539, 635, 720, 1000, 1200, 
        1400, 1600, 1800, 2050, 2300, 2500, 2800, 3200, 3600, 4031, 4567 ]
phan_focused_time = [ 0, 2, 23, 66, 143, 201, 252, 299, 359, 420, 443, 487, 539, 2500, 4031, 4567 ]
big_picture_time = [ 0, 66, 252, 539, 2500, 4031, 4567 ]

# colormaps to be used for colorbars
smallest_division = ListedColormap(smallest_division_colors)
phan_focused = ListedColormap(phan_focused_colors)
big_picture = ListedColormap(big_picture_colors)
phanerozoic = ListedColormap(smallest_division_colors[:16])

# label masks for colorbar plotting
smallest_division_mask = [ 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, # phanerozoic labels
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]
phan_focused_mask = [ 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1 ]
big_picture_mask = [ 1, 1, 1, 1, 1, 1, 1 ]
phanerozoic_mask = [ 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]

# plot colorbars
# plot_colorbars([smallest_division, phan_focused, big_picture, phanerozoic], 
#                [smallest_division_time, phan_focused_time, big_picture_time, smallest_division_time[:17]], 
#                [smallest_division_mask, phan_focused_mask, big_picture_mask, phanerozoic_mask],
#                ["Smallest Division", "Phan Focused", "Big Picture", "Phanerozoic"])

# norms and masks for colormaps used in draw_map_gui
smallest_division_norm = BoundaryNorm(smallest_division_time, smallest_division.N)
def c(value):
    return smallest_division(smallest_division_norm(value))
smallest_division_mask = [ 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, # phanerozoic labels
        0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1 ]

# geo_age_array = zip_time_and_color(smallest_division_colors, smallest_division_time)
