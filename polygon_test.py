# def set_pyproj_path(proj_path):
#     from pyproj import datadir
#     datadir.set_data_dir(proj_path)
# set_pyproj_path("/Users/emmahavens/opt/anaconda3/pkgs/proj-9.3.1-h81faed2_0/share/proj/proj.db")
import pyproj
# print(pyproj.datadir.get_data_dir())
import shapely
import shapely.ops
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.path import Path
from matplotlib.text import TextPath
import matplotlib.patches as patches
import cartopy.mpl.patch as cmp

from file_handling import Record

def transform(points):
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:4978", always_xy=True)
            
    lons = [record.along for record in points]
    lats = [record.alat for record in points]
    heights = [0] * len(points)
    x, y, z = transformer.transform(lons, lats, heights)
    coords = list(zip(x, y, z))
    r_coords = [ [round(x, 2), round(y, 2), round(z, 2)] for x, y, z in coords ]
    # print(f"coordinates:\n {np.array(r_coords)}")

    return r_coords

def transform_back(cartesian_polys):
    polys = []
    for cartesian_poly in cartesian_polys:
        ext_coords = np.array(cartesian_poly.exterior.coords)
        # print(f"results:\n {ext_coords}")
        # print(ext_coords[:,2])
        transformer = pyproj.Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)
        lons, lats, _ = transformer.transform(ext_coords[:,0], ext_coords[:,1], ext_coords[:,2])
        coords = fix_coords(list(zip(lons, lats)))
        polys.append(shapely.Polygon(coords))
    return polys


def fix_coords(coords):
    # figure out if pos or neg poly
    print("\nbefore:")
    print(coords)
    for lon, _ in coords:
        found_solution = True
        if lon not in [180, -180, 0]:
            poly_is_pos = lon > 0
            break
        found_solution = False
    if not found_solution: return
    if poly_is_pos: fixed_coords = [ (abs(lon), lat) for lon, lat in coords ]
    else: fixed_coords = [(-abs(lon), lat) for lon, lat in coords ]
    print("fixed:")
    print(fixed_coords)

    # add pole points

    return fixed_coords
    

def make_poly(coords):
    cartesian_poly = shapely.Polygon(coords)

    dateline_plane = shapely.Polygon([(0, 0, 10000000), (-10000000, 0, 10000000), 
                                      (-10000000, 0, -10000000), (0, 0, -10000000)])
    hemi_divider = shapely.LineString([(10000000, 0, 0), (-10000000, 0, 0)])
    
    intersection = shapely.intersection(cartesian_poly, dateline_plane)
    if not intersection.is_empty:
        geo_coll = shapely.ops.split(cartesian_poly, hemi_divider)
        cartesian_polys = []
        [ cartesian_polys.append(geom) for geom in geo_coll.geoms ]
        print(f"split in {len(cartesian_polys)}")
        return cartesian_polys

    return [cartesian_poly]

def divide(points):
    coords = transform(points)
    cartesian_polys = make_poly(coords)
    polys = transform_back(cartesian_polys)
    return polys

def path_to_records(path):
        records = []
        for point in path.vertices:
            record = Record(point[1], point[0], 2)
            records.append(record)
        return records

north_pole = [Record(80, 0, 3),
              Record(80, 90, 2),
              Record(80, 180, 2),
              Record(80, -90, 2)]
path1 = Path([(-160, 30), (-180, 30), (-180, 60), (-160, 60), (-160, 30)])
superdate = Path([(-170, 35), (170, 35), (170, 20), (-175, 20), (-175, 15), (170, 15), (170, 10),
                       (-170, 10), (-170, 25), (175, 25), (175, 30), (-170, 30), (-170, 35)])
# # polys = divide(north_pole)
# polys = divide(path_to_records(superdate))
# print(polys)

fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mollweide(central_longitude=0)})
# # # fig, ax = plt.subplots(subplot_kw={'projection': ccrs.NorthPolarStereo(central_longitude=180)})

# ax.add_geometries(polys, crs=ccrs.PlateCarree(),  # what about at the pole?
#                             facecolor=['blue', 'red', 'pink', 'yellow'], edgecolor='pink', linewidth=1)

# ax.text(0,0,"a")
ax.set_global()
patha = TextPath((0,0), "a")
cartopatch = cmp.path_to_geos(Path(patha.vertices, patha.codes))
ax.add_patch(patches.PathPatch(patha, transform=ccrs.PlateCarree(), facecolor='blue', edgecolor='pink', linewidth=1))
# ax.add_geometries(cartopatch, crs=ccrs.PlateCarree(), facecolor=['blue', 'red', 'pink', 'yellow'], edgecolor='pink', linewidth=1)
plt.show()

# test_plane = shapely.Polygon([(1,1,0),(1,-1,0),(-1,-1,0),(-1, 1,0)])
# test_line = shapely.LineString([(0,0,1),(0,0,-1)])
# non_line = shapely.LineString([(2,2,1), (2,2,-1)])
# test_point = shapely.Point(0,0,1)
# print(shapely.intersection(test_plane, test_point))

# Problems:
# - Shapely doesn't do computations in 3d space.
#     - A nonissue with the current goal but it's still stupid
# - When pyproj back converts to coordinates, it doesn't respect the proper sign(+/-) 
#   for creating projectable polygons
#     - Possibly solved
# - When dividing the polygons, it doesn't add points across the pole
# - It interprets the polygons as 'flat' instead of curving to the globe
#     - Seems to be a serious issue. Coordinates did not re-project well and seem distorted

