from matplotlib import pyplot as plt
from matplotlib import rc_context as mplrc_context
import numpy as np
import cartopy.crs as ccrs
import cartopy.mpl.patch as cmp
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.gridspec import GridSpec
from matplotlib.colors import is_color_like, CSS4_COLORS, Normalize
from matplotlib.animation import FFMpegWriter
from matplotlib import rcParams as mplrcParams
import matplotlib.cm as mplcm
import shapely.geometry
import shapely.ops as ops
import os
import sys

import timeline_colormap_creation as tcc

class Figure:

    def __init__(self, proj_select, **kwargs):

        self.ax = None
        self.set_color_list()
        self.proj = proj_select

        # animation fields
        self.frame_count = 0
        if "fps" in kwargs: self.fps = kwargs["fps"]

        lat_space = kwargs["lat_spacing"]
        lon_space = kwargs["lon_spacing"]

        match self.proj:
            case 0:     # Rectilinear projection
                self.set_Rectilinear(lat_space, lon_space, kwargs)
            case 1:     # Orthographic projection
                self.set_Orthographic(lat_space, lon_space, kwargs)
            case 2:     # Robinson projection
                self.set_Robinson(lat_space, lon_space, kwargs)
            case 3:     # Mollweide projection
                self.set_Mollweide(lat_space, lon_space, kwargs)
            case 4:     # Mercator projection
                self.set_Mercator(lat_space, lon_space, kwargs)
            case 5:     # Transverse Mercator projection
                self.set_Transverse_Mercator(lat_space, lon_space, kwargs)
            case 6:     # Miller projection
                self.set_Miller(lat_space, lon_space, kwargs)
            case 7:     # Azimuthal Equidistant projection
                self.set_Azimuthal(lat_space, lon_space, kwargs)    
            case 8:     # Stereographic projection
                self.set_Stereographic(lat_space, lon_space, kwargs)
        
        self.fig.set_size_inches(15, 10)
        self.fig.tight_layout()
        self.fig.canvas.draw()
        self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)
        # Get 2D vertices from boundary (drop z-coordinate if present)
        vertices = np.array(self.ax.projection.boundary.coords)[:,:2]  # Shape (N,2)
        
        # Convert to matplotlib Path
        self.clip_path = Path(vertices, closed=True)

    def set_Mollweide(self, lat_space, lon_space, kwargs):
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': ccrs.Mollweide(central_longitude=0)})
        self.ax.set_extent(kwargs["map_bounds"])
        self.draw_gridlines(lat_space, lon_space, 'moll')        

    def set_Robinson(self, lat_space, lon_space, kwargs):
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': ccrs.Robinson(central_longitude=0)})
        self.ax.set_extent(kwargs["map_bounds"])
        self.draw_gridlines(lat_space, lon_space, 'rob')

    def set_Miller(self, lat_space, lon_space, kwargs):
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': ccrs.Miller(central_longitude=0)})
        self.ax.set_extent(kwargs["map_bounds"])
        self.draw_gridlines(lat_space, lon_space, 'mill')

    def set_Mercator(self, lat_space, lon_space, kwargs):
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()})
        self.ax.set_extent(kwargs["map_bounds"])
        self.draw_gridlines(lat_space, lon_space, 'merc')
    
    def set_Rectilinear(self, lat_space, lon_space, kwargs):
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        self.ax.set_extent(kwargs["map_bounds"])
        self.draw_gridlines(lat_space, lon_space, 'cyl')

    def set_Orthographic(self, lat_space, lon_space, kwargs):
        center_lon = kwargs["center_lon"]
        center_lat = kwargs["center_lat"]
        self.fig, self.ax = plt.subplots(
            subplot_kw={'projection': ccrs.Orthographic(central_longitude=center_lon, central_latitude=center_lat)})
        self.ax.set_global()
        self.draw_gridlines(lat_space, lon_space, 'ortho')

    def set_Azimuthal(self, lat_space, lon_space, kwargs):
        center_lon = kwargs["center_lon"]
        center_lat = kwargs["center_lat"]
        self.fig, self.ax = plt.subplots(
            subplot_kw={'projection': ccrs.AzimuthalEquidistant(central_longitude=center_lon, central_latitude=center_lat)})
        self.ax.set_global()
        self.draw_gridlines(lat_space, lon_space, 'azim')

    def set_Transverse_Mercator(self, lat_space, lon_space, kwargs):
        center_lon = kwargs["center_lon"]
        center_lat = kwargs["center_lat"]
        self.fig, self.ax = plt.subplots(
            subplot_kw={'projection': ccrs.TransverseMercator(central_longitude=center_lon, central_latitude=center_lat)})
        self.ax.set_global()
        self.draw_gridlines(lat_space, lon_space, 'trans')

    def set_Stereographic(self, lat_space, lon_space, kwargs):    
        # Set up the polar projection
        if kwargs["north_hemi"]:
            self.fig, self.ax = plt.subplots(subplot_kw={'projection': ccrs.NorthPolarStereo(central_longitude=180)})
            self.ax.set_extent([-180, 180, kwargs["min_lat"], 90], crs=ccrs.PlateCarree())
        else:
            self.fig, self.ax = plt.subplots(subplot_kw={'projection': ccrs.SouthPolarStereo(central_longitude=180)})
            self.ax.set_extent([-180, 180, -90, kwargs["min_lat"]], crs=ccrs.PlateCarree())
    
        # Draw gridlines
        self.draw_gridlines(lat_space, lon_space, 'stereo')

    
    def draw_gridlines(self, lat_space, lon_space, projection):
        """
        Draw parallels and meridians with labels.
        """
        parallels = np.arange(-90, 120, lat_space)
        meridians = np.arange(-420, 420, lon_space)
        
        if projection in ['moll', 'ortho', 'azim']:
            # Draw gridlines with labels
            self.ax.gridlines(xlocs=meridians, ylocs=parallels, draw_labels=True, 
                linestyle='--', color='gray', xlabel_style={'alpha': 0})
        elif projection in ['stereo', 'trans']:
            gl = self.ax.gridlines(xlocs=meridians, ylocs=[], draw_labels=True, rotate_labels=False,
                linestyle='--', color='gray')
            self.ax.gridlines(xlocs=[], ylocs=parallels, draw_labels=False, 
                linestyle='--', color='gray')
            
            gl.top_labels
        else:
            # Draw gridlines with labels
            self.ax.gridlines(xlocs=meridians, ylocs=parallels, draw_labels=True, 
                linestyle='--', color='gray')
        
        # elif projection in ['merc', 'cyl']:

    def update_plot_vars(self, output_tuple, plot_time):
        self.output = output_tuple
        self.plot_time = plot_time
        self.ax.set_title(f"{plot_time}Ma", loc="left")
        self.fig.tight_layout()

    def set_color_list(self):
       light_colors = [ "whitesmoke", "white", "snow", "mistyrose", "seashell", "linen", "bisque",
                        "antiquewhite", "navajowhite", "blanchedalmond", "papayawhip", "moccasin", "wheat",
                         "oldlace", "floralwhite", "cornsilk", "lemonchiffon", "ivory", "beige", "lightyellow",
                         "lightgoldenrodyellow", "honeydew", "mintcream", "azure", "lightcyan", "aliceblue", 
                         "ghostwhite", "lavender", "lavenderblush" ]
       all_colors = list(CSS4_COLORS)
       self.color_list = [color for color in all_colors if color not in light_colors]
       
       self.ocean_age_norm = Normalize(0, 250)
       self.ocean_age_cmap = mplcm.rainbow_r
       self.ocean_age_colorbar = False
       
       self.geo_age_norm = tcc.smallest_division_norm
       self.geo_age_cmap = tcc.smallest_division
       self.geo_age_colorbar = False

    def check_if_special_color(self, color, age, plateid):
        if color == "multicolor":
            rand_index = np.random.randint(1, len(self.color_list))
            color = self.color_list[rand_index]
        elif color == "byGeoAge":
            color = self.geo_age_cmap(self.geo_age_norm(age))
            self.geo_age_colorbar = True
        elif color == "byOceanAge":
            chunk_age = age - self.plot_time
            color = self.ocean_age_cmap(self.ocean_age_norm(chunk_age))
            self.ocean_age_colorbar = True

        return color
    
    def add_colorbars(self):
        colorbars = []
        if self.geo_age_colorbar:
            colorbars.append((self.geo_age_norm, self.geo_age_cmap))
        if self.ocean_age_colorbar:
            colorbars.append((self.ocean_age_norm, self.ocean_age_cmap))
        
        if not colorbars:
            return  # No colorbars to add
        
        # Calculate new figure height (original height + space for colorbars)
        fig_dim = self.fig.get_size_inches()
        new_height = fig_dim[1] + 0.5 * len(colorbars)  # 0.5 inches per colorbar
        self.fig.set_size_inches(fig_dim[0], new_height)
        
        # Create GridSpec with space for main content and colorbars
        self.gs = self.fig.add_gridspec(nrows=1 + len(colorbars), ncols=1, 
                                height_ratios=[fig_dim[1]] + [0.5]*len(colorbars))
        
        # Move all existing axes to the top grid slot
        existing_axes = self.fig.axes
        for ax in existing_axes:
            ax.set_subplotspec(self.gs[0])
        
        # Add colorbars in the remaining grid slots
        for i, (norm, cmap) in enumerate(colorbars, 1):
            cb_ax = self.fig.add_subplot(self.gs[i])
            self.fig.colorbar(
                mplcm.ScalarMappable(norm=norm, cmap=cmap),
                cax=cb_ax, 
                orientation='horizontal', 
                extend='neither', 
                spacing='proportional'
            )
            # cb_ax.set_ylabel(name)
        
        # Adjust layout to prevent overlap
        self.fig.tight_layout()
        
    def process_records(self, records):
        # Build path with anti-meridian handling
        vertices = []
        codes = []
        prev_lon = None
        for record in records:
            alat = record.alat
            along = record.along
            pen = record.pen
            
            # Handle antimeridian crossing
            dateline_crossing = prev_lon and abs(along - prev_lon) > 180
            if dateline_crossing:
                corrected_lon = along + 360 if prev_lon > 0 else along - 360
                # corrected_lon = round(corrected_lon, 1)
                vertices.append((corrected_lon, alat))
                codes.append(Path.LINETO if (pen == 2 and len(vertices) > 1) else Path.MOVETO)
            else:
                vertices.append((along, alat))
                codes.append(Path.LINETO if (pen == 2 and len(vertices) > 1) else Path.MOVETO)
                prev_lon = along

        return vertices, codes    

    def max_lat(self, list):
        return max(list[0][1], list[-1][1]) # lats of first and last points
    
    def split_polygons(self, poly_list):
        meridians = [0, 180, -180]
        sections = [[]]
        prev_meridian = False
        cur_section = 0
        
        # Divide list by artificial meridian points
        for point in poly_list:
            lon = point[0]
            if lon in meridians and prev_meridian:
                sections.append([point])
                cur_section += 1
                prev_meridian = False
            elif lon in meridians:
                sections[cur_section].append(point)
                prev_meridian = True
            else:
                sections[cur_section].append(point)
                prev_meridian = False

        # # combine first and last lists if there is a non-meridian starting point
        if len(sections) > 1 and not (sections[0][0][0] in meridians):
            [ sections[-1].append(point) for point in sections[0] ]
            sections.pop(0)

        # combine into polygons
        complete = False
        while not complete:
            complete = True
            sections.sort(reverse=True, key=self.max_lat)
            for i, section in enumerate(sections[:-1]):
                start_lat = min(section[0][1], section[-1][1])
                end_lat = max(section[0][1], section[-1][1])
                next_lat = sections[i + 1][0][1]
                if start_lat < next_lat and next_lat < end_lat:
                    if end_lat > start_lat:
                        # if it crosses the pole, add polar points
                        end_lon = sections[i][-1][0]
                        start_lon = sections[i + 1][0][0]
                        if end_lon != start_lon:
                            pole_lat = 90 if start_lat > 0 else -90
                            sections[i].append((end_lon, pole_lat))
                            sections[i].append((start_lon, pole_lat))
                        # combine sections
                        [ sections[i].append(point) for point in sections[i + 1] ]
                        sections.pop(i + 1)
                    else:
                        # if it crosses the pole, add polar points
                        end_lon = sections[i + 1][-1][0]
                        start_lon = sections[i][0][0]
                        if end_lon != start_lon:
                            pole_lat = 90 if start_lat > 0 else -90
                            sections[i].append((end_lon, pole_lat))
                            sections[i].append((start_lon, pole_lat))
                        # combine sections
                        [ sections[i + 1].append(point) for point in sections[i] ]
                        sections.pop(i)
                    complete = False
                    break

        # make each polygon completed
        for i in range(len(sections)):
            start_point = sections[i][0]
            sections[i].append(start_point)
            # if this creates a pole crossing, add polar points
            if sections[i][-2][0] in meridians and sections[i][-2][0] != sections[i][-1][0]:
                pole_lat = 90 if sections[i][-2][1] > 0 else -90
                sections[i].insert(-1, (sections[i][-2][0], pole_lat))
                sections[i].insert(-1, (sections[i][-1][0], pole_lat))
    
        return sections
    
    def process_polygons(self, records):
        positive = []
        negative = []
        prev_lon = records[0].along
        prev_lat = records[0].alat
        for record in records:
            lat = record.alat
            lon = record.along
            # pen = record["pen"]

            # integer values reserved for meridian points in splitting algorithm
            if lon == 180: lon = 180.001
            elif lon == -180: lon = -180.001
            elif lon == 0 and prev_lon > 0: lon = 0.001
            elif lon == 0 and prev_lon < 0: lon = -0.001

            if prev_lon != 0 and lon/prev_lon < 0:
                if abs(lon - prev_lon) > 180:
                    mid_lon = 180 if prev_lon > 0 else -180
                    # mid_lat = lat + (prev_lat - lat) * (mid_lon - prev_lon)/(lon - prev_lon)
                    lon_dist = abs(mid_lon - prev_lon) + abs(-mid_lon - lon)
                    lon_dist = -lon_dist if prev_lon < 0 else lon_dist
                    mid_lat = prev_lat + (mid_lon - prev_lon) * (lat - prev_lat)/lon_dist
                    positive.append((180, mid_lat))
                    negative.append((-180, mid_lat))
                else:
                    mid_lat = prev_lat + (0 - prev_lon) * (lat - prev_lat)/(lon - prev_lon)
                    positive.append((0, mid_lat))
                    negative.append((0, mid_lat))
            if lon > 0:
                positive.append((lon, lat))
            else:
                negative.append((lon, lat))
            
            prev_lon = lon
            prev_lat = lat

        # delete duplicate point
        if prev_lon > 0:
            positive.pop(-1)
        else:
            negative.pop(-1)

        if positive and negative:
            pos_polys = self.split_polygons(positive)
            neg_polys = self.split_polygons(negative)
            [ pos_polys.append(poly) for poly in neg_polys ]
            return pos_polys
        elif positive:
            positive.append(positive[0])
            return [positive]
        else:
            negative.append(negative[0])
            return [negative]
        
    # def path_to_records(self, path):
    #     records = []
    #     for point in path.vertices:
    #         record = {"alat": point[1], "along": point[0]}
    #         records.append(record)
    #     return records

    def plot_to_screen(self, chunk_generator):
        for coll in self.ax.collections:
            coll.remove()
        for patch in self.ax.patches:
            patch.remove()
        self.fig.canvas.restore_region(self.bg)
        
        shapes = []
        collectable = True
        first_loop = True
        border_color = "none"
        fill_color = "none"

        one_by_one = False  # only for troubleshooting
        
        for chunk in chunk_generator:
            
             # read in border color
            color = self.check_if_special_color(chunk.border_color, chunk.appears, chunk.plateid)
            if not is_color_like(color) or color == "1":
                bcolor = "black"
            else:
                bcolor = color

            # read in fill color
            color = self.check_if_special_color(chunk.fill_color, chunk.appears, chunk.plateid)
            if not is_color_like(color) or color == "1" or len(chunk.records) < 3:
                fcolor = "none"
            else:
                fcolor = color

            # determine collectability
            if bcolor != border_color or fcolor != fill_color:
                if first_loop: 
                    first_loop = False
                    border_color = bcolor
                    fill_color = fcolor
                else: 
                    collectable = False

            # if it is not collectable anymore, plot everything collected and start over
            if not collectable and shapes: # len(shapes) > 50
                self.ax.add_geometries(shapes, crs=ccrs.PlateCarree(), facecolor=fill_color, edgecolor=border_color)
                border_color = bcolor
                fill_color = fcolor

                # plt.draw()  # Force immediate render
                # self.fig.canvas.flush_events()  # Process pending GUI events
                # plt.pause(0.001)  # Allow GUI event processing
                # one_by_one = True
                # print("plot many")

                # reset variables
                shapes.clear()
                collectable = True
            
            # finish creating next shape
            if fill_color != "none":
                polygon_list = self.process_polygons(chunk.records)
                try:
                    shape_list = [ shapely.Polygon(poly) for poly in polygon_list ]
                except ValueError:
                    print("unresolvable polygon, trying again as lines")
                    vertices, codes = self.process_records(chunk.records)
                    shape_list = cmp.path_to_geos(Path(vertices, codes))
            else:
                vertices, codes = self.process_records(chunk.records)
                shape_list = cmp.path_to_geos(Path(vertices, codes))

            # Add shape to list
            [ shapes.append(shape) for shape in shape_list ]

            yield chunk
            
            # only for troubleshooting
            if one_by_one:
                print("next iter")
                vertices, codes = self.process_records(chunk.records)
                path = Path(vertices, codes)
                self.ax.add_geometries(shapes, crs=ccrs.PlateCarree(), facecolor=fill_color, edgecolor=border_color)
                print("PATH")
                print(path)
                plt.draw()  # Force immediate render
                self.fig.canvas.flush_events()  # Process pending GUI events
                # plt.pause(0.001)  # Allow GUI event processing
                plt.pause(0.5)
                one_by_one = True
                shapes.clear()

        # plot everything that hasn't been plotted
        if shapes:
            self.ax.add_geometries(shapes, crs=ccrs.PlateCarree(), facecolor=fill_color, edgecolor=border_color)
            # pass
        if not hasattr(self, 'gs'):
            self.add_colorbars()
    
    #region Troubleshooting
    #     path1 = Path([(-160, 30), (-180, 30), (-180, 60), (-160, 60), (-160, 30)])
    #     path2 = Path([(-160, 30), (160, 30), (160, 60), (-160, 60), (-160, 30)])
    #     ohio = Path([(-160, 10), (-160, 30), (160, 30), (-170, 20), (160, 10), (-160, 10)])
    #     supers = Path([(-160, 35), (-180, 35), (-180, 20), (-165, 20), (-165, 15), (-180, 15), (-180, 10),
    #                    (-160, 10), (-160, 25), (-175, 25), (-175, 30), (-160, 30), (-160, 35)])
    #     superdate = Path([(-170, 35), (170, 35), (170, 20), (-175, 20), (-175, 15), (170, 15), (170, 10),
    #                    (-170, 10), (-170, 25), (175, 25), (175, 30), (-170, 30), (-170, 35)])
    #     superplus = Path([(-170, 35), (-190, 35), (-190, 20), (-175, 20), (-175, 15), (-190, 15), (-190, 10),
    #                    (-170, 10), (-170, 25), (-185, 25), (-185, 30), (-170, 30), (-170, 35)])
    #     meridian = Path([(-10, -10), (-10, 10), (10, 10), (10, -10), (-10, -10)])
    #     pole = Path([(20, -80), (160, -80), (-160, -80), (-20, -80), (20, -80)])
    #     pole_half = Path([(0.01, -80.0), (20.0, -80.0), (160.0, -80.0), (180, -80.0), (180, -90), (0.01, -90), (0.01, -80.0)])
    #     crescent = Path([(45, 80), (-90, 80), (120, 80), (-135, 86), (85, 82), (-30, 86), (45 ,80)])
    #     first_problem = Path([[-1.800000e+02,  8.993400e+01],
    #    [ 0.000000e+00,  8.990000e+01],
    #    [ 0.000000e+00,  8.990000e+01],
    #    [ 1.800000e+02,  8.993400e+01],
    #    [ 1.335350e+02,  8.882700e+01],
    #    [ 1.340793e+02,  8.841400e+01],
    #    [ 1.330691e+02,  8.793430e+01],
    #    [ 1.340620e+02,  8.755980e+01],
    #    [ 1.352163e+02,  8.721230e+01],
    #    [ 1.356582e+02,  8.700120e+01],
    #    [ 1.356582e+02,  8.700120e+01],
    #    [ 1.363714e+02,  8.664460e+01],
    #    [ 1.370641e+02,  8.617920e+01],
    #    [ 1.374478e+02,  8.580420e+01],
    #    [ 1.379161e+02,  8.541950e+01],
    #    [ 1.384064e+02,  8.518100e+01],
    #    [ 1.389074e+02,  8.487720e+01],
    #    [ 1.392180e+02,  8.442790e+01],
    #    [ 1.393578e+02,  8.365480e+01],
    #    [ 1.394710e+02,  8.275220e+01],
    #    [ 1.394241e+02,  8.204890e+01],
    #    [ 1.393329e+02,  8.144110e+01],
    #    [ 1.394511e+02,  8.093460e+01],
    #    [ 1.394784e+02,  8.029350e+01],
    #    [ 1.393489e+02,  7.948520e+01],
    #    [ 1.388621e+02,  7.921900e+01],
    #    [ 1.382848e+02,  7.906720e+01],
    #    [ 1.377647e+02,  7.898720e+01],
    #    [ 1.370390e+02,  7.888190e+01],
    #    [ 1.363264e+02,  7.883210e+01],
    #    [ 1.355850e+02,  7.879520e+01],
    #    [ 1.348877e+02,  7.875200e+01],
    #    [ 1.342462e+02,  7.867400e+01],
    #    [ 1.333356e+02,  7.855640e+01],
    #    [ 1.326569e+02,  7.846240e+01],
    #    [ 1.321205e+02,  7.832470e+01],
    #    [ 1.313868e+02,  7.818290e+01],
    #    [ 1.307457e+02,  7.798960e+01],
    #    [ 1.301075e+02,  7.789730e+01],
    #    [ 1.296192e+02,  7.783810e+01],
    #    [ 1.289097e+02,  7.775340e+01],
    #    [ 1.284596e+02,  7.770500e+01],
    #    [ 1.276876e+02,  7.763420e+01],
    #    [ 1.267865e+02,  7.754960e+01],
    #    [ 1.259318e+02,  7.732860e+01],
    #    [ 1.258520e+02,  7.799390e+01],
    #    [ 1.251413e+02,  7.848120e+01],
    #    [ 1.239888e+02,  7.915390e+01],
    #    [ 1.226157e+02,  7.992480e+01],
    #    [ 1.213753e+02,  8.064570e+01],
    #    [ 1.200858e+02,  8.125620e+01],
    #    [ 1.186450e+02,  8.201850e+01],
    #    [ 1.165431e+02,  8.280610e+01],
    #    [ 1.147165e+02,  8.345980e+01],
    #    [ 1.117523e+02,  8.400000e+01],
    #    [ 1.097370e+02,  8.412220e+01],
    #    [ 1.073188e+02,  8.427110e+01],
    #    [ 1.043904e+02,  8.457420e+01],
    #    [ 1.022898e+02,  8.481200e+01],
    #    [ 9.984270e+01,  8.508540e+01],
    #    [ 9.771450e+01,  8.518950e+01],
    #    [ 9.488390e+01,  8.511860e+01],
    #    [ 9.250970e+01,  8.524340e+01],
    #    [ 9.069490e+01,  8.532420e+01],
    #    [ 8.853090e+01,  8.537360e+01],
    #    [ 8.576450e+01,  8.551350e+01],
    #    [ 8.329760e+01,  8.556320e+01],
    #    [ 8.092680e+01,  8.577760e+01],
    #    [ 7.875430e+01,  8.589470e+01],
    #    [ 7.683130e+01,  8.608070e+01],
    #    [ 7.352660e+01,  8.623000e+01],
    #    [ 7.172340e+01,  8.632160e+01],
    #    [ 6.876390e+01,  8.640150e+01],
    #    [ 6.652370e+01,  8.650990e+01],
    #    [ 6.468560e+01,  8.656920e+01],
    #    [ 6.266170e+01,  8.675910e+01],
    #    [ 6.007200e+01,  8.682480e+01],
    #    [ 5.791240e+01,  8.669450e+01],
    #    [ 5.529120e+01,  8.681750e+01],
    #    [ 5.360400e+01,  8.671400e+01],
    #    [ 5.156290e+01,  8.674740e+01],
    #    [ 4.927360e+01,  8.674550e+01],
    #    [ 4.735100e+01,  8.665090e+01],
    #    [ 4.541210e+01,  8.671410e+01],
    #    [ 4.322280e+01,  8.668590e+01],
    #    [ 4.069080e+01,  8.650250e+01],
    #    [ 3.858900e+01,  8.641490e+01],
    #    [ 3.685900e+01,  8.636900e+01],
    #    [ 3.495980e+01,  8.629600e+01],
    #    [ 3.310310e+01,  8.616530e+01],
    #    [ 3.146030e+01,  8.604880e+01],
    #    [ 2.898740e+01,  8.594170e+01],
    #    [ 2.676660e+01,  8.597080e+01],
    #    [ 2.505610e+01,  8.584570e+01],
    #    [ 2.337530e+01,  8.591020e+01],
    #    [ 2.180520e+01,  8.593680e+01],
    #    [ 2.044510e+01,  8.587680e+01],
    #    [ 1.928450e+01,  8.575300e+01],
    #    [ 1.771230e+01,  8.572350e+01],
    #    [ 1.614620e+01,  8.555920e+01],
    #    [ 1.421330e+01,  8.548750e+01],
    #    [ 1.230150e+01,  8.538130e+01],
    #    [ 1.038970e+01,  8.527510e+01],
    #    [ 8.555500e+00,  8.514350e+01],
    #    [ 7.088100e+00,  8.491930e+01],
    #    [ 5.813700e+00,  8.475500e+01],
    #    [ 4.408700e+00,  8.469670e+01],
    #    [ 3.253300e+00,  8.470730e+01],
    #    [ 2.372800e+00,  8.457280e+01],
    #    [ 1.465200e+00,  8.431590e+01],
    #    [ 7.386000e-01,  8.438860e+01],
    #    [ 1.853000e-01,  8.403480e+01],
    #    [-6.321000e-01,  8.383150e+01],
    #    [-1.757000e+00,  8.376550e+01],
    #    [-2.645900e+00,  8.370340e+01],
    #    [-3.243200e+00,  8.363220e+01],
    #    [-4.155000e+00,  8.355950e+01],
    #    [-5.396200e+00,  8.336240e+01],
    #    [-6.963400e+00,  8.297340e+01],
    #    [-6.089500e+00,  8.273280e+01],
    #    [-4.809500e+00,  8.219330e+01],
    #    [-3.806300e+00,  8.138940e+01],
    #    [-2.423800e+00,  8.110280e+01],
    #    [-3.102400e+00,  8.058500e+01],
    #    [-2.455500e+00,  8.044880e+01],
    #    [-1.819700e+00,  8.040180e+01],
    #    [-1.255900e+00,  8.020740e+01],
    #    [-3.020000e-01,  8.001480e+01],
    #    [ 5.521000e-01,  7.985910e+01],
    #    [ 1.150700e+00,  7.978990e+01],
    #    [ 2.348500e+00,  7.967400e+01],
    #    [ 3.321900e+00,  7.956500e+01],
    #    [ 4.228700e+00,  7.923730e+01],
    #    [ 3.835500e+00,  7.875180e+01],
    #    [ 4.816700e+00,  7.853040e+01],
    #    [ 5.409100e+00,  7.844450e+01],
    #    [ 6.346500e+00,  7.825810e+01],
    #    [ 7.261700e+00,  7.808360e+01],
    #    [ 7.850400e+00,  7.775840e+01],
    #    [ 7.763400e+00,  7.688900e+01],
    #    [ 7.681700e+00,  7.624600e+01],
    #    [ 7.997700e+00,  7.539960e+01],
    #    [ 8.810900e+00,  7.465000e+01],
    #    [ 9.347000e+00,  7.402140e+01],
    #    [ 9.333600e+00,  7.358950e+01],
    #    [ 9.119600e+00,  7.320880e+01],
    #    [ 8.634800e+00,  7.314540e+01],
    #    [ 8.004900e+00,  7.310880e+01],
    #    [ 7.284200e+00,  7.304150e+01],
    #    [ 6.528100e+00,  7.291910e+01],
    #    [ 5.760800e+00,  7.279710e+01],
    #    [ 5.093700e+00,  7.264940e+01],
    #    [ 4.416500e+00,  7.253580e+01],
    #    [ 3.728000e+00,  7.242250e+01],
    #    [ 3.153200e+00,  7.235060e+01],
    #    [ 2.407200e+00,  7.219420e+01],
    #    [ 1.709700e+00,  7.214860e+01],
    #    [ 9.203000e-01,  7.203850e+01],
    #    [ 3.060000e-02,  7.195390e+01],
    #    [-7.476000e-01,  7.184350e+01],
    #    [-1.481200e+00,  7.172040e+01],
    #    [-2.224400e+00,  7.165370e+01],
    #    [-2.957300e+00,  7.155300e+01],
    #    [-3.814400e+00,  7.143380e+01],
    #    [-4.846000e+00,  7.129760e+01],
    #    [-5.700300e+00,  7.144770e+01],
    #    [-6.378500e+00,  7.130040e+01],
    #    [-7.016400e+00,  7.111350e+01],
    #    [-7.665700e+00,  7.107110e+01],
    #    [-8.237400e+00,  7.110010e+01],
    #    [-9.502200e+00,  7.122940e+01],
    #    [-1.035050e+01,  7.139050e+01],
    #    [-1.120820e+01,  7.160820e+01],
    #    [-1.169330e+01,  7.109140e+01],
    #    [-1.212330e+01,  7.053070e+01],
    #    [-1.276460e+01,  7.066860e+01],
    #    [-1.330300e+01,  7.068540e+01],
    #    [-1.376770e+01,  7.078590e+01],
    #    [-1.417270e+01,  7.052160e+01],
    #    [-1.468040e+01,  7.026240e+01],
    #    [-1.531570e+01,  6.987230e+01],
    #    [-1.590600e+01,  6.930690e+01],
    #    [-1.663640e+01,  6.883570e+01],
    #    [-1.759860e+01,  6.831540e+01],
    #    [-1.826250e+01,  6.755020e+01],
    #    [-1.879070e+01,  6.657290e+01],
    #    [-1.940600e+01,  6.652150e+01],
    #    [-2.019660e+01,  6.666900e+01],
    #    [-2.066500e+01,  6.660010e+01],
    #    [-2.076810e+01,  6.704150e+01],
    #    [-2.144550e+01,  6.713170e+01],
    #    [-2.216830e+01,  6.707320e+01],
    #    [-2.321070e+01,  6.703170e+01],
    #    [-2.428020e+01,  6.690270e+01],
    #    [-2.496860e+01,  6.667900e+01],
    #    [-2.544900e+01,  6.644890e+01],
    #    [-2.603530e+01,  6.616210e+01],
    #    [-2.658640e+01,  6.572730e+01],
    #    [-2.693240e+01,  6.509370e+01],
    #    [-2.621700e+01,  6.478250e+01],
    #    [-2.551390e+01,  6.473400e+01],
    #    [-2.489460e+01,  6.481920e+01],
    #    [-2.438740e+01,  6.478190e+01],
    #    [-2.473700e+01,  6.434040e+01],
    #    [-2.431560e+01,  6.401390e+01],
    #    [-2.445230e+01,  6.348110e+01],
    #    [-2.378460e+01,  6.330620e+01],
    #    [-2.442320e+01,  6.298150e+01],
    #    [-2.497040e+01,  6.271790e+01],
    #    [-2.561950e+01,  6.242370e+01],
    #    [-2.656030e+01,  6.195900e+01],
    #    [-2.733360e+01,  6.146660e+01],
    #    [-2.781520e+01,  6.114480e+01],
    #    [-2.834130e+01,  6.083560e+01],
    #    [-2.874410e+01,  6.052260e+01],
    #    [-2.934070e+01,  6.011440e+01],
    #    [-2.981310e+01,  5.972500e+01],
    #    [-3.047880e+01,  5.926290e+01],
    #    [-3.108290e+01,  5.879330e+01],
    #    [-3.222730e+01,  5.809920e+01],
    #    [-3.268180e+01,  5.774840e+01],
    #    [-3.319970e+01,  5.734360e+01],
    #    [-3.355370e+01,  5.688620e+01],
    #    [-3.410140e+01,  5.669230e+01],
    #    [-3.456270e+01,  5.684140e+01],
    #    [-3.544920e+01,  5.685790e+01],
    #    [-3.612360e+01,  5.683400e+01],
    #    [-3.729130e+01,  5.683670e+01],
    #    [-3.821390e+01,  5.677560e+01],
    #    [-3.916770e+01,  5.679410e+01],
    #    [-4.026100e+01,  5.665980e+01],
    #    [-4.124010e+01,  5.658930e+01],
    #    [-4.251710e+01,  5.668520e+01],
    #    [-4.372610e+01,  5.680150e+01],
    #    [-4.480290e+01,  5.683510e+01],
    #    [-4.578410e+01,  5.669720e+01],
    #    [-4.689600e+01,  5.668700e+01],
    #    [-4.807030e+01,  5.683590e+01],
    #    [-4.918750e+01,  5.701670e+01],
    #    [-5.048380e+01,  5.721430e+01],
    #    [-5.118410e+01,  5.743820e+01],
    #    [-5.205880e+01,  5.783600e+01],
    #    [-5.257690e+01,  5.814410e+01],
    #    [-5.322610e+01,  5.856850e+01],
    #    [-5.388550e+01,  5.902700e+01],
    #    [-5.472580e+01,  5.944620e+01],
    #    [-5.539850e+01,  5.983770e+01],
    #    [-5.629170e+01,  6.035950e+01],
    #    [-5.720630e+01,  6.091580e+01],
    #    [-5.838480e+01,  6.164870e+01],
    #    [-5.945190e+01,  6.235560e+01],
    #    [-6.042660e+01,  6.314390e+01],
    #    [-6.046890e+01,  6.376840e+01],
    #    [-5.988120e+01,  6.479430e+01],
    #    [-5.936280e+01,  6.557530e+01],
    #    [-5.851950e+01,  6.669430e+01],
    #    [-5.786160e+01,  6.762820e+01],
    #    [-5.766550e+01,  6.815540e+01],
    #    [-5.801030e+01,  6.862090e+01],
    #    [-5.854520e+01,  6.910910e+01],
    #    [-5.923510e+01,  6.966960e+01],
    #    [-5.988190e+01,  7.017250e+01],
    #    [-6.065000e+01,  7.074670e+01],
    #    [-6.139910e+01,  7.120790e+01],
    #    [-6.247420e+01,  7.165690e+01],
    #    [-6.338360e+01,  7.202210e+01],
    #    [-6.414850e+01,  7.233780e+01],
    #    [-6.518150e+01,  7.269570e+01],
    #    [-6.587070e+01,  7.291930e+01],
    #    [-6.661730e+01,  7.309970e+01],
    #    [-6.745440e+01,  7.326060e+01],
    #    [-6.865760e+01,  7.356200e+01],
    #    [-6.972630e+01,  7.385910e+01],
    #    [-7.095850e+01,  7.431300e+01],
    #    [-7.207990e+01,  7.471840e+01],
    #    [-7.301300e+01,  7.503950e+01],
    #    [-7.391360e+01,  7.532580e+01],
    #    [-7.484780e+01,  7.561310e+01],
    #    [-7.543480e+01,  7.587180e+01],
    #    [-7.470690e+01,  7.617020e+01],
    #    [-7.410820e+01,  7.628620e+01],
    #    [-7.350700e+01,  7.648080e+01],
    #    [-7.303150e+01,  7.667450e+01],
    #    [-7.248520e+01,  7.666410e+01],
    #    [-7.194200e+01,  7.660540e+01],
    #    [-7.143170e+01,  7.648280e+01],
    #    [-7.040160e+01,  7.624200e+01],
    #    [-6.950490e+01,  7.608260e+01],
    #    [-6.880120e+01,  7.597790e+01],
    #    [-6.813820e+01,  7.585500e+01],
    #    [-6.733010e+01,  7.571700e+01],
    #    [-6.670340e+01,  7.567100e+01],
    #    [-6.565630e+01,  7.550900e+01],
    #    [-6.466970e+01,  7.521600e+01],
    #    [-6.390760e+01,  7.503460e+01],
    #    [-6.319810e+01,  7.494850e+01],
    #    [-6.271300e+01,  7.489850e+01],
    #    [-6.189460e+01,  7.480690e+01],
    #    [-6.133690e+01,  7.466760e+01],
    #    [-6.064250e+01,  7.442800e+01],
    #    [-6.017740e+01,  7.425430e+01],
    #    [-5.975770e+01,  7.402600e+01],
    #    [-5.935690e+01,  7.381980e+01],
    #    [-5.891880e+01,  7.347500e+01],
    #    [-5.859360e+01,  7.289000e+01],
    #    [-5.819390e+01,  7.245460e+01],
    #    [-5.761170e+01,  7.206560e+01],
    #    [-5.699440e+01,  7.176960e+01],
    #    [-5.639090e+01,  7.138080e+01],
    #    [-5.594440e+01,  7.104940e+01],
    #    [-5.639090e+01,  7.043210e+01],
    #    [-5.686700e+01,  6.992890e+01],
    #    [-5.667390e+01,  6.943700e+01],
    #    [-5.647290e+01,  6.865530e+01],
    #    [-5.662920e+01,  6.798720e+01],
    #    [-5.658040e+01,  6.728980e+01],
    #    [-5.644580e+01,  6.682300e+01],
    #    [-5.607120e+01,  6.619990e+01],
    #    [-5.561340e+01,  6.571160e+01],
    #    [-5.522070e+01,  6.537900e+01],
    #    [-5.470460e+01,  6.492370e+01],
    #    [-5.398810e+01,  6.444370e+01],
    #    [-5.345290e+01,  6.444180e+01],
    #    [-5.309150e+01,  6.484160e+01],
    #    [-5.286290e+01,  6.453070e+01],
    #    [-5.284060e+01,  6.400140e+01],
    #    [-5.264170e+01,  6.347340e+01],
    #    [-5.230200e+01,  6.304510e+01],
    #    [-5.171540e+01,  6.265600e+01],
    #    [-5.091090e+01,  6.236830e+01],
    #    [-5.048180e+01,  6.194950e+01],
    #    [-5.038780e+01,  6.153120e+01],
    #    [-4.969140e+01,  6.117570e+01],
    #    [-4.893930e+01,  6.079860e+01],
    #    [-4.836260e+01,  6.045360e+01],
    #    [-4.767650e+01,  6.024680e+01],
    #    [-4.697280e+01,  6.014990e+01],
    #    [-4.636900e+01,  5.989590e+01],
    #    [-4.576610e+01,  5.950580e+01],
    #    [-4.501050e+01,  5.940500e+01],
    #    [-4.424830e+01,  5.941000e+01],
    #    [-4.368010e+01,  5.951400e+01],
    #    [-4.300030e+01,  5.979240e+01],
    #    [-4.239270e+01,  6.043260e+01],
    #    [-4.201010e+01,  6.109290e+01],
    #    [-4.185780e+01,  6.158510e+01],
    #    [-4.173520e+01,  6.234730e+01],
    #    [-4.127940e+01,  6.297370e+01],
    #    [-4.072670e+01,  6.345670e+01],
    #    [-4.027750e+01,  6.387110e+01],
    #    [-3.975880e+01,  6.427160e+01],
    #    [-3.918270e+01,  6.462990e+01],
    #    [-3.871250e+01,  6.492760e+01],
    #    [-3.828540e+01,  6.521130e+01],
    #    [-3.771380e+01,  6.534510e+01],
    #    [-3.704000e+01,  6.534400e+01],
    #    [-3.649800e+01,  6.555240e+01],
    #    [-3.567610e+01,  6.586070e+01],
    #    [-3.477690e+01,  6.622830e+01],
    #    [-3.420630e+01,  6.648350e+01],
    #    [-3.350880e+01,  6.685130e+01],
    #    [-3.279080e+01,  6.727050e+01],
    #    [-3.220050e+01,  6.754810e+01],
    #    [-3.171830e+01,  6.774120e+01],
    #    [-3.104570e+01,  6.792030e+01],
    #    [-3.033620e+01,  6.807420e+01],
    #    [-2.950380e+01,  6.827820e+01],
    #    [-2.886400e+01,  6.835950e+01],
    #    [-2.830040e+01,  6.844930e+01],
    #    [-2.753680e+01,  6.852910e+01],
    #    [-2.705420e+01,  6.856230e+01],
    #    [-2.656180e+01,  6.857620e+01],
    #    [-2.592290e+01,  6.870200e+01],
    #    [-2.529690e+01,  6.888320e+01],
    #    [-2.452490e+01,  6.910250e+01],
    #    [-2.367090e+01,  6.942250e+01],
    #    [-2.312620e+01,  6.964310e+01],
    #    [-2.253330e+01,  6.990430e+01],
    #    [-2.192720e+01,  7.022220e+01],
    #    [-2.129960e+01,  7.082030e+01],
    #    [-2.065300e+01,  7.120050e+01],
    #    [-1.974080e+01,  7.118860e+01],
    #    [-1.896080e+01,  7.124020e+01],
    #    [-1.845500e+01,  7.140980e+01],
    #    [-1.787320e+01,  7.178900e+01],
    #    [-1.739750e+01,  7.211740e+01],
    #    [-1.687360e+01,  7.237200e+01],
    #    [-1.623010e+01,  7.268460e+01],
    #    [-1.556690e+01,  7.312420e+01],
    #    [-1.486920e+01,  7.368790e+01],
    #    [-1.413640e+01,  7.397020e+01],
    #    [-1.338140e+01,  7.431960e+01],
    #    [-1.294920e+01,  7.452130e+01],
    #    [-1.243960e+01,  7.473460e+01],
    #    [-1.166460e+01,  7.493720e+01],
    #    [-1.096470e+01,  7.517210e+01],
    #    [-1.010300e+01,  7.541180e+01],
    #    [-9.335700e+00,  7.561460e+01],
    #    [-8.526500e+00,  7.581620e+01],
    #    [-7.580800e+00,  7.608160e+01],
    #    [-6.847700e+00,  7.627800e+01],
    #    [-5.940800e+00,  7.661770e+01],
    #    [-5.512700e+00,  7.673560e+01],
    #    [-5.042800e+00,  7.690280e+01],
    #    [-4.438200e+00,  7.721730e+01],
    #    [-4.018300e+00,  7.799970e+01],
    #    [-4.043600e+00,  7.884180e+01],
    #    [-4.091800e+00,  7.937630e+01],
    #    [-4.254200e+00,  7.988090e+01],
    #    [-4.587400e+00,  8.019180e+01],
    #    [-5.049900e+00,  8.066850e+01],
    #    [-5.589000e+00,  8.090870e+01],
    #    [-6.242600e+00,  8.112290e+01],
    #    [-7.087100e+00,  8.133140e+01],
    #    [-7.876900e+00,  8.150900e+01],
    #    [-8.690200e+00,  8.167950e+01],
    #    [-9.491000e+00,  8.182480e+01],
    #    [-1.032890e+01,  8.193130e+01],
    #    [-1.122260e+01,  8.205550e+01],
    #    [-1.229870e+01,  8.220440e+01],
    #    [-1.286690e+01,  8.229540e+01],
    #    [-1.354160e+01,  8.241380e+01],
    #    [-1.415710e+01,  8.254370e+01],
    #    [-1.542520e+01,  8.284350e+01],
    #    [-1.636010e+01,  8.300630e+01],
    #    [-1.749850e+01,  8.314460e+01],
    #    [-1.855960e+01,  8.324100e+01],
    #    [-1.938470e+01,  8.332340e+01],
    #    [-2.036270e+01,  8.341750e+01],
    #    [-2.084030e+01,  8.353860e+01],
    #    [-2.175330e+01,  8.386960e+01],
    #    [-2.117640e+01,  8.415710e+01],
    #    [-2.029160e+01,  8.424630e+01],
    #    [-1.968430e+01,  8.431290e+01],
    #    [-1.895300e+01,  8.439210e+01],
    #    [-1.818090e+01,  8.448690e+01],
    #    [-1.682230e+01,  8.462730e+01],
    #    [-1.537980e+01,  8.478830e+01],
    #    [-1.424130e+01,  8.494010e+01],
    #    [-1.337590e+01,  8.504430e+01],
    #    [-1.293640e+01,  8.496730e+01],
    #    [-1.254500e+01,  8.531760e+01],
    #    [-1.316860e+01,  8.542080e+01],
    #    [-1.417290e+01,  8.545860e+01],
    #    [-1.491880e+01,  8.546420e+01],
    #    [-1.623110e+01,  8.547690e+01],
    #    [-1.736050e+01,  8.545840e+01],
    #    [-1.836090e+01,  8.541520e+01],
    #    [-1.980300e+01,  8.528720e+01],
    #    [-2.042370e+01,  8.526520e+01],
    #    [-2.226160e+01,  8.520070e+01],
    #    [-2.478180e+01,  8.507770e+01],
    #    [-2.675050e+01,  8.494330e+01],
    #    [-2.759580e+01,  8.493000e+01],
    #    [-2.910550e+01,  8.492230e+01],
    #    [-3.057000e+01,  8.483950e+01],
    #    [-3.168920e+01,  8.476010e+01],
    #    [-3.251020e+01,  8.470820e+01],
    #    [-3.373160e+01,  8.463970e+01],
    #    [-3.461950e+01,  8.462020e+01],
    #    [-3.551040e+01,  8.458650e+01],
    #    [-3.631040e+01,  8.455910e+01],
    #    [-3.730450e+01,  8.451400e+01],
    #    [-3.813010e+01,  8.441750e+01],
    #    [-3.976630e+01,  8.443000e+01],
    #    [-4.091220e+01,  8.465980e+01],
    #    [-4.179710e+01,  8.463280e+01],
    #    [-4.238570e+01,  8.461370e+01],
    #    [-4.374840e+01,  8.460610e+01],
    #    [-4.447480e+01,  8.460390e+01],
    #    [-4.566660e+01,  8.462520e+01],
    #    [-4.715850e+01,  8.465440e+01],
    #    [-4.928460e+01,  8.465480e+01],
    #    [-5.062790e+01,  8.464900e+01],
    #    [-5.167230e+01,  8.463960e+01],
    #    [-5.239830e+01,  8.476710e+01],
    #    [-5.194420e+01,  8.507810e+01],
    #    [-5.143780e+01,  8.516120e+01],
    #    [-5.085710e+01,  8.525200e+01],
    #    [-5.002750e+01,  8.542980e+01],
    #    [-4.949700e+01,  8.555120e+01],
    #    [-4.865410e+01,  8.572470e+01],
    #    [-4.780600e+01,  8.608340e+01],
    #    [-4.732850e+01,  8.678190e+01],
    #    [-4.710410e+01,  8.724660e+01],
    #    [-4.758480e+01,  8.753680e+01],
    #    [-4.814890e+01,  8.761980e+01],
    #    [-4.902240e+01,  8.771940e+01],
    #    [-5.080720e+01,  8.782380e+01],
    #    [-5.172380e+01,  8.787970e+01],
    #    [-5.238460e+01,  8.809250e+01],
    #    [-5.190090e+01,  8.856380e+01],
    #    [-5.190830e+01,  8.905350e+01],
    #    [-1.800000e+02,  8.993400e+01]])
    #     fp_abridged =Path([(180, 89), (138, 79), (125, 77), (-6, 82), (9, 73), (-38, 56), 
    #                        (-55, 57), (-73, 76), (-42, 60), (1, 73), (-50, 84), (180, 89)])
    #     abridged_rewind = Path([(180, 89), (-50, 84), (1, 73), (-42, 60), (-73, 76), 
    #                             (-55, 57), (-38, 56), (9, 73), (-6, 82), (125, 77), (138, 79), (180, 89)])
    #     problem346 = Path([[179.0263, -45.4354],
    #    [178.6958, -46.1421],
    #    [178.001 , -45.9843],
    #    [177.0321, -45.9514],
    #    [176.2365, -45.9321],
    #    [175.5645, -45.9021],
    #    [174.6297, -45.8421],
    #    [173.7954, -45.7988],
    #    [173.2128, -45.7854],
    #    [172.6305, -45.7562],
    #    [171.9583, -45.734 ],
    #    [171.4439, -45.39  ],
    #    [172.0029, -44.888 ],
    #    [172.587 , -44.5383],
    #    [173.2728, -44.2385],
    #    [173.7293, -43.8474],
    #    [173.3913, -43.364 ],
    #    [173.4135, -42.5776],
    #    [174.1142, -42.3323],
    #    [174.8073, -42.1353],
    #    [175.7532, -41.9026],
    #    [176.4519, -41.7002],
    #    [177.0809, -41.4844],
    #    [180.1, -45.2233],
    #    [179.0263, -45.4354]])
    #     final_boss = Path([[-1.796898e+02, -7.343530e+01],
    #    [-1.789699e+02, -7.365560e+01],
    #    [-1.781901e+02, -7.395880e+01],
    #    [-1.776192e+02, -7.416270e+01],
    #    [-1.770202e+02, -7.438400e+01],
    #    [-1.764658e+02, -7.451910e+01],
    #    [-1.761537e+02, -7.489640e+01],
    #    [-1.765354e+02, -7.554580e+01],
    #    [-1.769141e+02, -7.616560e+01],
    #    [-1.772677e+02, -7.686750e+01],
    #    [-1.777051e+02, -7.765240e+01],
    #    [-1.779815e+02, -7.827470e+01],
    #    [-1.782285e+02, -7.878990e+01],
    #    [-1.783238e+02, -7.964930e+01],
    #    [-1.780924e+02, -8.047580e+01],
    #    [-1.776667e+02, -8.076690e+01],
    #    [-1.769928e+02, -8.100670e+01],
    #    [-1.763100e+02, -8.115700e+01],
    #    [-1.756830e+02, -8.129010e+01],
    #    [-1.744005e+02, -8.149810e+01],
    #    [-1.732571e+02, -8.163250e+01],
    #    [-1.716877e+02, -8.180670e+01],
    #    [-1.705640e+02, -8.190720e+01],
    #    [-1.687796e+02, -8.205660e+01],
    #    [-1.673387e+02, -8.214760e+01],
    #    [-1.657758e+02, -8.223640e+01],
    #    [-1.644494e+02, -8.231170e+01],
    #    [-1.630058e+02, -8.238520e+01],
    #    [-1.614946e+02, -8.245200e+01],
    #    [-1.597432e+02, -8.250960e+01],
    #    [-1.581563e+02, -8.255780e+01],
    #    [-1.569418e+02, -8.257910e+01],
    #    [-1.551672e+02, -8.260810e+01],
    #    [-1.533227e+02, -8.263260e+01],
    #    [-1.510226e+02, -8.265070e+01],
    #    [-1.493270e+02, -8.263190e+01],
    #    [-1.485637e+02, -8.261340e+01],
    #    [-1.469810e+02, -8.258660e+01],
    #    [-1.458493e+02, -8.255850e+01],
    #    [-1.443221e+02, -8.251130e+01],
    #    [-1.431617e+02, -8.247180e+01],
    #    [-1.425617e+02, -8.256760e+01],
    #    [-1.422531e+02, -8.304720e+01],
    #    [-1.416983e+02, -8.325400e+01],
    #    [-1.408481e+02, -8.354260e+01],
    #    [-1.402030e+02, -8.374770e+01],
    #    [-1.390438e+02, -8.392510e+01],
    #    [-1.378103e+02, -8.409210e+01],
    #    [-1.363429e+02, -8.424110e+01],
    #    [-1.348719e+02, -8.433910e+01],
    #    [-1.332703e+02, -8.442540e+01],
    #    [-1.316982e+02, -8.451530e+01],
    #    [-1.300361e+02, -8.459670e+01],
    #    [-1.284216e+02, -8.470200e+01],
    #    [-1.270063e+02, -8.483350e+01],
    #    [-1.258595e+02, -8.491870e+01],
    #    [-1.252541e+02, -8.504750e+01],
    #    [-1.248185e+02, -8.509520e+01],
    #    [-1.222210e+02, -8.499350e+01],
    #    [-1.195365e+02, -8.491800e+01],
    #    [-1.149370e+02, -8.475580e+01],
    #    [-1.119739e+02, -8.460630e+01],
    #    [-1.097548e+02, -8.448170e+01],
    #    [-1.082470e+02, -8.438730e+01],
    #    [-1.073701e+02, -8.434040e+01],
    #    [-1.063840e+02, -8.427400e+01],
    #    [-1.054448e+02, -8.430690e+01],
    #    [-1.039649e+02, -8.438220e+01],
    #    [-1.029470e+02, -8.444200e+01],
    #    [-9.955150e+01, -8.462520e+01],
    #    [-9.623950e+01, -8.470110e+01],
    #    [-9.379580e+01, -8.473570e+01],
    #    [-9.101670e+01, -8.475050e+01],
    #    [-8.871350e+01, -8.475340e+01],
    #    [-8.749800e+01, -8.476260e+01],
    #    [-8.670400e+01, -8.477120e+01],
    #    [-8.569360e+01, -8.474640e+01],
    #    [-8.443870e+01, -8.462790e+01],
    #    [-8.163060e+01, -8.460270e+01],
    #    [-7.893240e+01, -8.448440e+01],
    #    [-7.589780e+01, -8.432710e+01],
    #    [-7.380780e+01, -8.418260e+01],
    #    [-7.253280e+01, -8.409360e+01],
    #    [-7.119540e+01, -8.399840e+01],
    #    [-6.996480e+01, -8.391420e+01],
    #    [-6.825030e+01, -8.381810e+01],
    #    [-6.627540e+01, -8.368440e+01],
    #    [-6.475670e+01, -8.359890e+01],
    #    [-6.316700e+01, -8.348450e+01],
    #    [-6.159100e+01, -8.336270e+01],
    #    [-6.066190e+01, -8.323630e+01],
    #    [-5.936380e+01, -8.307710e+01],
    #    [-5.799790e+01, -8.284640e+01],
    #    [-5.653450e+01, -8.270180e+01],
    #    [-5.486840e+01, -8.256330e+01],
    #    [-5.267830e+01, -8.235630e+01],
    #    [-5.077730e+01, -8.226210e+01],
    #    [-4.924750e+01, -8.208850e+01],
    #    [-4.741070e+01, -8.200340e+01],
    #    [-4.591220e+01, -8.188140e+01],
    #    [-4.459770e+01, -8.176140e+01],
    #    [-4.335230e+01, -8.145380e+01],
    #    [-4.174430e+01, -8.123420e+01],
    #    [-4.101740e+01, -8.100700e+01],
    #    [-3.986280e+01, -8.071910e+01],
    #    [-3.857730e+01, -8.031910e+01],
    #    [-3.796750e+01, -7.975490e+01],
    #    [-3.787160e+01, -7.897590e+01],
    #    [-3.759760e+01, -7.815880e+01],
    #    [-3.701150e+01, -7.769370e+01],
    #    [-3.615030e+01, -7.739280e+01],
    #    [-3.510390e+01, -7.708600e+01],
    #    [-3.402660e+01, -7.672100e+01],
    #    [-3.337220e+01, -7.648580e+01],
    #    [-3.223050e+01, -7.608700e+01],
    #    [-3.168600e+01, -7.584620e+01],
    #    [-3.091350e+01, -7.545570e+01],
    #    [-3.024760e+01, -7.506540e+01],
    #    [-2.936840e+01, -7.471160e+01],
    #    [-2.883410e+01, -7.462320e+01],
    #    [-2.831020e+01, -7.458200e+01],
    #    [-2.753350e+01, -7.449360e+01],
    #    [-2.675430e+01, -7.418800e+01],
    #    [-2.599420e+01, -7.401020e+01],
    #    [-2.508600e+01, -7.399820e+01],
    #    [-2.450320e+01, -7.390660e+01],
    #    [-2.381600e+01, -7.367390e+01],
    #    [-2.305100e+01, -7.345920e+01],
    #    [-2.222630e+01, -7.334600e+01],
    #    [-2.158060e+01, -7.328400e+01],
    #    [-2.079320e+01, -7.330200e+01],
    #    [-2.015670e+01, -7.316560e+01],
    #    [-1.936000e+01, -7.308590e+01],
    #    [-1.872080e+01, -7.291710e+01],
    #    [-1.811960e+01, -7.260810e+01],
    #    [-1.762060e+01, -7.240350e+01],
    #    [-1.699660e+01, -7.219000e+01],
    #    [-1.611260e+01, -7.196010e+01],
    #    [-1.551280e+01, -7.174480e+01],
    #    [-1.495300e+01, -7.157390e+01],
    #    [-1.398710e+01, -7.133950e+01],
    #    [-1.316690e+01, -7.116440e+01],
    #    [-1.247320e+01, -7.101590e+01],
    #    [-1.166670e+01, -7.080760e+01],
    #    [-1.078500e+01, -7.060990e+01],
    #    [-1.032760e+01, -7.044910e+01],
    #    [-9.682500e+00, -7.032320e+01],
    #    [-9.005200e+00, -7.032090e+01],
    #    [-8.358000e+00, -7.030260e+01],
    #    [-7.601300e+00, -7.027680e+01],
    #    [-6.802900e+00, -7.022270e+01],
    #    [-5.910100e+00, -7.020540e+01],
    #    [-5.170500e+00, -7.019040e+01],
    #    [-4.064100e+00, -7.018690e+01],
    #    [-3.123700e+00, -7.016920e+01],
    #    [-2.126900e+00, -7.011070e+01],
    #    [-1.313600e+00, -7.003230e+01],
    #    [-6.931000e-01, -6.994520e+01],
    #    [ 3.840000e-02, -6.983870e+01],
    #    [ 7.992000e-01, -6.988170e+01],
    #    [ 1.891200e+00, -6.986930e+01],
    #    [ 2.812300e+00, -6.984470e+01],
    #    [ 3.714600e+00, -6.976320e+01],
    #    [ 4.740500e+00, -6.975550e+01],
    #    [ 5.762100e+00, -6.971540e+01],
    #    [ 6.545600e+00, -6.971930e+01],
    #    [ 7.706600e+00, -6.965720e+01],
    #    [ 8.463100e+00, -6.957510e+01],
    #    [ 9.137000e+00, -6.959040e+01],
    #    [ 9.809800e+00, -6.961010e+01],
    #    [ 1.043360e+01, -6.932070e+01],
    #    [ 1.071160e+01, -6.891980e+01],
    #    [ 1.110530e+01, -6.837680e+01],
    #    [ 1.070710e+01, -6.765560e+01],
    #    [ 1.097320e+01, -6.731580e+01],
    #    [ 1.149870e+01, -6.748540e+01],
    #    [ 1.198470e+01, -6.789410e+01],
    #    [ 1.250390e+01, -6.854850e+01],
    #    [ 1.323980e+01, -6.894240e+01],
    #    [ 1.399120e+01, -6.905120e+01],
    #    [ 1.477560e+01, -6.907040e+01],
    #    [ 1.581770e+01, -6.912070e+01],
    #    [ 1.665370e+01, -6.913760e+01],
    #    [ 1.738930e+01, -6.919980e+01],
    #    [ 1.842810e+01, -6.940470e+01],
    #    [ 1.887560e+01, -6.966100e+01],
    #    [ 1.935360e+01, -6.980330e+01],
    #    [ 2.019280e+01, -6.990760e+01],
    #    [ 2.142350e+01, -6.996010e+01],
    #    [ 2.242870e+01, -6.996420e+01],
    #    [ 2.343780e+01, -6.994570e+01],
    #    [ 2.426300e+01, -6.991400e+01],
    #    [ 2.500390e+01, -6.988410e+01],
    #    [ 2.572150e+01, -6.986620e+01],
    #    [ 2.651860e+01, -6.981360e+01],
    #    [ 2.715470e+01, -6.972960e+01],
    #    [ 2.756180e+01, -6.928580e+01],
    #    [ 2.812500e+01, -6.914400e+01],
    #    [ 2.905990e+01, -6.909660e+01],
    #    [ 2.993570e+01, -6.899290e+01],
    #    [ 3.070090e+01, -6.862870e+01],
    #    [ 3.126450e+01, -6.799870e+01],
    #    [ 3.165330e+01, -6.749710e+01],
    #    [ 3.209210e+01, -6.690100e+01],
    #    [ 3.249680e+01, -6.646040e+01],
    #    [ 3.279680e+01, -6.606470e+01],
    #    [ 3.332740e+01, -6.587850e+01],
    #    [ 3.404610e+01, -6.583140e+01],
    #    [ 3.452610e+01, -6.599140e+01],
    #    [ 3.495630e+01, -6.635950e+01],
    #    [ 3.468660e+01, -6.687510e+01],
    #    [ 3.435080e+01, -6.734490e+01],
    #    [ 3.474030e+01, -6.765470e+01],
    #    [ 3.507780e+01, -6.818340e+01],
    #    [ 3.604850e+01, -6.826490e+01],
    #    [ 3.686970e+01, -6.840670e+01],
    #    [ 3.766670e+01, -6.843370e+01],
    #    [ 3.823580e+01, -6.842220e+01],
    #    [ 3.886520e+01, -6.824440e+01],
    #    [ 3.965290e+01, -6.809160e+01],
    #    [ 4.028850e+01, -6.797550e+01],
    #    [ 4.069290e+01, -6.791890e+01],
    #    [ 4.130610e+01, -6.786750e+01],
    #    [ 4.221330e+01, -6.766310e+01],
    #    [ 4.292000e+01, -6.749250e+01],
    #    [ 4.358540e+01, -6.734650e+01],
    #    [ 4.455330e+01, -6.713050e+01],
    #    [ 4.552470e+01, -6.692000e+01],
    #    [ 4.656750e+01, -6.673220e+01],
    #    [ 4.759360e+01, -6.653100e+01],
    #    [ 4.853700e+01, -6.637750e+01],
    #    [ 4.946040e+01, -6.612850e+01],
    #    [ 5.062180e+01, -6.584260e+01],
    #    [ 5.176570e+01, -6.562210e+01],
    #    [ 5.249520e+01, -6.550640e+01],
    #    [ 5.317290e+01, -6.543210e+01],
    #    [ 5.400290e+01, -6.543450e+01],
    #    [ 5.485670e+01, -6.547020e+01],
    #    [ 5.545780e+01, -6.551660e+01],
    #    [ 5.628750e+01, -6.563550e+01],
    #    [ 5.726130e+01, -6.588780e+01],
    #    [ 5.809590e+01, -6.619930e+01],
    #    [ 5.880600e+01, -6.641930e+01],
    #    [ 5.942550e+01, -6.652300e+01],
    #    [ 6.005130e+01, -6.659820e+01],
    #    [ 6.085520e+01, -6.663870e+01],
    #    [ 6.158710e+01, -6.660080e+01],
    #    [ 6.219950e+01, -6.661210e+01],
    #    [ 6.322340e+01, -6.665470e+01],
    #    [ 6.414210e+01, -6.670290e+01],
    #    [ 6.492850e+01, -6.673520e+01],
    #    [ 6.590750e+01, -6.679360e+01],
    #    [ 6.698920e+01, -6.681960e+01],
    #    [ 6.776520e+01, -6.687780e+01],
    #    [ 6.846230e+01, -6.676000e+01],
    #    [ 6.896940e+01, -6.658220e+01],
    #    [ 6.971910e+01, -6.655720e+01],
    #    [ 7.066020e+01, -6.656900e+01],
    #    [ 7.170670e+01, -6.658270e+01],
    #    [ 7.309940e+01, -6.660600e+01],
    #    [ 7.419260e+01, -6.669790e+01],
    #    [ 7.510910e+01, -6.678280e+01],
    #    [ 7.576630e+01, -6.680130e+01],
    #    [ 7.664100e+01, -6.674700e+01],
    #    [ 7.755780e+01, -6.668350e+01],
    #    [ 7.842190e+01, -6.652830e+01],
    #    [ 7.895840e+01, -6.637920e+01],
    #    [ 7.972900e+01, -6.612890e+01],
    #    [ 8.070990e+01, -6.579970e+01],
    #    [ 8.182050e+01, -6.564090e+01],
    #    [ 8.257220e+01, -6.563380e+01],
    #    [ 8.366980e+01, -6.563860e+01],
    #    [ 8.463340e+01, -6.570750e+01],
    #    [ 8.529470e+01, -6.573500e+01],
    #    [ 8.604500e+01, -6.581010e+01],
    #    [ 8.662250e+01, -6.576970e+01],
    #    [ 8.733490e+01, -6.570810e+01],
    #    [ 8.798490e+01, -6.564420e+01],
    #    [ 8.886170e+01, -6.557190e+01],
    #    [ 8.944620e+01, -6.550740e+01],
    #    [ 9.007100e+01, -6.541130e+01],
    #    [ 9.088350e+01, -6.524660e+01],
    #    [ 9.155840e+01, -6.514080e+01],
    #    [ 9.243350e+01, -6.502030e+01],
    #    [ 9.321300e+01, -6.493510e+01],
    #    [ 9.411560e+01, -6.480720e+01],
    #    [ 9.490560e+01, -6.462100e+01],
    #    [ 9.561180e+01, -6.438410e+01],
    #    [ 9.623390e+01, -6.438440e+01],
    #    [ 9.687220e+01, -6.423200e+01],
    #    [ 9.737680e+01, -6.405180e+01],
    #    [ 9.771700e+01, -6.406450e+01],
    #    [ 9.832260e+01, -6.402000e+01],
    #    [ 9.921110e+01, -6.392090e+01],
    #    [ 1.000197e+02, -6.397840e+01],
    #    [ 1.005171e+02, -6.405570e+01],
    #    [ 1.005171e+02, -6.405570e+01],
    #    [ 1.010712e+02, -6.407790e+01],
    #    [ 1.018970e+02, -6.434760e+01],
    #    [ 1.030315e+02, -6.454470e+01],
    #    [ 1.040375e+02, -6.464760e+01],
    #    [ 1.053072e+02, -6.475990e+01],
    #    [ 1.066041e+02, -6.483610e+01],
    #    [ 1.074580e+02, -6.493130e+01],
    #    [ 1.081420e+02, -6.503590e+01],
    #    [ 1.087183e+02, -6.511400e+01],
    #    [ 1.096331e+02, -6.523380e+01],
    #    [ 1.102673e+02, -6.516460e+01],
    #    [ 1.110319e+02, -6.525900e+01],
    #    [ 1.121378e+02, -6.528250e+01],
    #    [ 1.135092e+02, -6.530580e+01],
    #    [ 1.146064e+02, -6.528440e+01],
    #    [ 1.155956e+02, -6.518990e+01],
    #    [ 1.162844e+02, -6.509040e+01],
    #    [ 1.168339e+02, -6.510530e+01],
    #    [ 1.175320e+02, -6.518370e+01],
    #    [ 1.185435e+02, -6.513240e+01],
    #    [ 1.194911e+02, -6.526990e+01],
    #    [ 1.200388e+02, -6.537590e+01],
    #    [ 1.208977e+02, -6.539910e+01],
    #    [ 1.215387e+02, -6.538660e+01],
    #    [ 1.227008e+02, -6.530410e+01],
    #    [ 1.232808e+02, -6.524080e+01],
    #    [ 1.242497e+02, -6.516020e+01],
    #    [ 1.251278e+02, -6.510670e+01],
    #    [ 1.258570e+02, -6.505170e+01],
    #    [ 1.266270e+02, -6.500640e+01],
    #    [ 1.279766e+02, -6.491400e+01],
    #    [ 1.291097e+02, -6.488660e+01],
    #    [ 1.302003e+02, -6.492410e+01],
    #    [ 1.309998e+02, -6.489860e+01],
    #    [ 1.322351e+02, -6.478730e+01],
    #    [ 1.335996e+02, -6.468430e+01],
    #    [ 1.341777e+02, -6.470700e+01],
    #    [ 1.354262e+02, -6.481040e+01],
    #    [ 1.363826e+02, -6.503890e+01],
    #    [ 1.373855e+02, -6.524440e+01],
    #    [ 1.383574e+02, -6.535450e+01],
    #    [ 1.393992e+02, -6.544550e+01],
    #    [ 1.401253e+02, -6.553090e+01],
    #    [ 1.409858e+02, -6.555480e+01],
    #    [ 1.416663e+02, -6.559860e+01],
    #    [ 1.423090e+02, -6.564910e+01],
    #    [ 1.435243e+02, -6.579650e+01],
    #    [ 1.443442e+02, -6.585860e+01],
    #    [ 1.449679e+02, -6.582930e+01],
    #    [ 1.459109e+02, -6.580630e+01],
    #    [ 1.470113e+02, -6.578220e+01],
    #    [ 1.478186e+02, -6.580810e+01],
    #    [ 1.486193e+02, -6.586990e+01],
    #    [ 1.493369e+02, -6.580820e+01],
    #    [ 1.502491e+02, -6.584880e+01],
    #    [ 1.508941e+02, -6.591650e+01],
    #    [ 1.518349e+02, -6.608740e+01],
    #    [ 1.525898e+02, -6.622700e+01],
    #    [ 1.530879e+02, -6.632780e+01],
    #    [ 1.538138e+02, -6.648350e+01],
    #    [ 1.551700e+02, -6.668190e+01],
    #    [ 1.559395e+02, -6.690190e+01],
    #    [ 1.565018e+02, -6.716250e+01],
    #    [ 1.571810e+02, -6.768590e+01],
    #    [ 1.576235e+02, -6.797070e+01],
    #    [ 1.583077e+02, -6.830770e+01],
    #    [ 1.588062e+02, -6.863300e+01],
    #    [ 1.595581e+02, -6.885940e+01],
    #    [ 1.604147e+02, -6.903080e+01],
    #    [ 1.610163e+02, -6.916350e+01],
    #    [ 1.616559e+02, -6.929220e+01],
    #    [ 1.625302e+02, -6.944590e+01],
    #    [ 1.635251e+02, -6.958540e+01],
    #    [ 1.643790e+02, -6.962340e+01],
    #    [ 1.655222e+02, -6.993830e+01],
    #    [ 1.665069e+02, -7.002270e+01],
    #    [ 1.675331e+02, -7.022310e+01],
    #    [ 1.684867e+02, -7.041560e+01],
    #    [ 1.693987e+02, -7.064680e+01],
    #    [ 1.701889e+02, -7.088940e+01],
    #    [ 1.710158e+02, -7.110580e+01],
    #    [ 1.717886e+02, -7.140890e+01],
    #    [ 1.723969e+02, -7.166280e+01],
    #    [ 1.731699e+02, -7.191730e+01],
    #    [ 1.740677e+02, -7.212350e+01],
    #    [ 1.748685e+02, -7.233830e+01],
    #    [ 1.757565e+02, -7.250680e+01],
    #    [ 1.767585e+02, -7.272970e+01],
    #    [ 1.775002e+02, -7.288640e+01],
    #    [ 1.786161e+02, -7.306450e+01],
    #    [ 1.797788e+02, -7.333070e+01],
    #    [ 1.803000e+02, -7.343530e+01],
    #    [-1.796898e+02, -7.343530e+01]])
    #     problem406 = Path([[-80.4311,  -8.0497],
    #    [-80.5351,  -7.7974],
    #    [-80.1564,  -8.7959],
    #    [-80.4311,  -8.0497]])

    #     records = self.path_to_records(problem406)
    #     polygons_list = self.process_polygons(records)
    #     print(polygons_list)
    #     polygons = [ shapely.Polygon(poly) for poly in polygons_list ]
    #     print(polygons)

    #     x_val = [p[0] for p in problem406.vertices]
    #     y_val = [p[1] for p in problem406.vertices]
    #     self.ax.add_geometries(polygons, crs=ccrs.PlateCarree(),  # what about at the pole?
    #                            facecolor=['blue', 'red', 'pink', 'yellow'], edgecolor='pink', linewidth=1)
    #     self.ax.scatter(x_val, y_val, edgecolors='y', transform=ccrs.PlateCarree(), zorder=10)
    #endregion 
        
        # print(self.output)
        if self.output["anim"]:
            png_name = ".anim" + str(self.frame_count) + ".png"
            self.fig.savefig(png_name, bbox_inches='tight', pad_inches=0.1)
            self.frame_count += 1
        if self.output["plot"]:
            plt.draw()  # Force immediate render
            self.fig.canvas.flush_events()  # Process pending GUI events
            plt.pause(0.5)  # Allow GUI event processing
        if self.output["save"]:
            pdf_name = self.output["save"] + ".pdf"
            plt.savefig(pdf_name, format='pdf')

    def make_animation(self, anim_name, frame_rate): 

        # Configure FFmpeg path for PyInstaller bundles
        ffmpeg_path = mplrcParams['animation.ffmpeg_path']
        if getattr(sys, 'frozen', False):
            bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg')
            
            # Verify the binary exists and is executable
            if not os.path.exists(ffmpeg_path):
                raise FileNotFoundError(f"FFmpeg not found at {ffmpeg_path}")
            
            # This is the critical line - sets the path matplotlib will use
            # mplrcParams['animation.ffmpeg_path'] = ffmpeg_path
        print(f"FFmpeg using path: {ffmpeg_path}")
        
        with mplrc_context({'animation.ffmpeg_path': ffmpeg_path}):
            writer = FFMpegWriter(fps=frame_rate, bitrate=5000)
            fig = plt.figure(frameon=False, layout='constrained')
            height_pix, width_pix = plt.imread(".anim0.png").shape[:2]
            width = width_pix / fig.get_dpi()
            height = height_pix / fig.get_dpi()
            print(f"{width, height}")
            fig.set_size_inches(width, height, forward=True) # need to set fig to be same aspect as pngs
            
            with writer.saving(fig, anim_name, dpi=300):
                for i in range(self.frame_count):
                    img = plt.imread(f".anim{i}.png")
                    os.remove(f".anim{i}.png")
                    plt.imshow(img)
                    plt.axis('off')
                    writer.grab_frame()
                    plt.clf()
