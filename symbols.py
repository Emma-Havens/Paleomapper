import csv
import math
import shapely.geometry as shapegeo
import numpy as np
from matplotlib.path import Path
from cartopy.mpl.patch import geos_to_path
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
from numpy import deg2rad


Shapes = [  "urn",
            "label",
            "circle",
            "dot",
            "triangle",
            "square",
            "plus",
            "cross",
            "storm",
            "asterisk",
            "diamond",
            "star",
            "dextral",
            "sinistral",
            "arrow01",
            "arrow02",
            "arrow03",
            "arrow04",
            "arrow05",
            "arrow06",
            "subduction",
            "normal",
            "conglomerate",
            "sand",
            "sandwmud",
            "mud",
            "mudwls",
            "lswmud",
            "limestone"]


global library

def load_shape_library(file_path):
    global library

    library = {}
    with open(file_path, 'r', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=',', fieldnames=['shape', 'x', 'y', 'pen'])
        for row in reader:
            # Convert numeric fields to floats/int
            shape_name = row['shape']
            x = float(row['x'])
            y = float(row['y'])
            pen = int(row['pen'])

            # Add the data to the dictionary
            if shape_name not in library:
                if shape_name not in Shapes:
                    print(f"Unidentified symbol in library: {shape_name}")
                library[shape_name] = {'x': [], 'y': [], 'pen': []}
            
            library[shape_name]['x'].append(x)
            library[shape_name]['y'].append(y)
            library[shape_name]['pen'].append(pen)

def create_circle(lat, lon, diameter):

    radius = diameter / 2

    # Larger radii will have higher resolution to maintain smoothness
    resolution = max(16, int(radius * 10))  # Adjust scaling factor as needed

    # Create a Shapely Point and buffer it to create a circle
    circle = shapegeo.Point(0, 0).buffer(radius, resolution=resolution)
    paths = geos_to_path(circle)
    circle_path = Path.make_compound_path(*paths)
    circle_path.vertices = rotate(circle_path.vertices, lat, lon)
    return circle_path

def create_symbol(lat, lon, size, azimuth, symbol):
    symbol_data = library.get(symbol)
    if not symbol_data:
        raise ValueError(f"{symbol} shape not found in the dictionary.")

    # Scale and translate the coordinates
    vertices = []
    codes = []
    for x, y, pen in zip(symbol_data['x'], symbol_data['y'], symbol_data['pen']):
        x_scaled = x * size
        y_scaled = y * size
        vertices.append((x_scaled, y_scaled))
        codes.append(Path.MOVETO if pen == 3 else Path.LINETO)

    rad = deg2rad(azimuth)
    transform = Affine2D().rotate_around(0, 0, rad)
    symbol_path = Path(vertices, codes).transformed(transform)
    symbol_path.vertices = rotate(symbol_path.vertices, lat, lon)
    return symbol_path

def create_text(lat, lon, size, azimuth, text):

    # find boundaries of text box
    text_size = size * 1.3
    init_text = TextPath((0, 0), text, size=text_size)

    rad = deg2rad(azimuth)
    rotation = Affine2D().rotate_around(0, 0, rad)
    rotated_text = init_text.transformed(rotation)

    bbox = rotated_text.get_extents()
    y_length = abs(bbox.ymax - bbox.ymin)
    x_length = abs(bbox.xmax - bbox.xmin)

    # find center point of text
    # y = lat - float(y_length / 2)
    # x = lon - float(x_length / 2)
    y = -float(y_length / 2)
    x = -float(x_length / 2)

    # return text placed at lat/lon
    transform = Affine2D().translate(x, y)
    text_path = rotated_text.transformed(transform)
    text_path.vertices = rotate(text_path.vertices, lat, lon)
    return text_path

def rotate(unrotated_list, dest_lat, dest_lon):
    first_rotation = [ rotate_point(lat, lon, 90, 0, dest_lon) for lon, lat in unrotated_list ]
    second_rotation = [ rotate_point(lat, lon, 0, 90 + dest_lon, -dest_lat) for lon, lat in first_rotation ]
    return second_rotation

def rotate_point(alat,along,rotlat,rotlo, rotan):
        d = .017453292519943

        if (alat == 90.0):
                alat=89.9     #/* handle the exceptions */
        if (alat == -90.0):
                alat=-89.9

        if (rotan == 0.0):
            anlat = alat
            anlong = along

        if (rotan != 0.0):
            a1=90.0*d-alat*d
            sina1=math.sin(a1)
            a2=along*d
            px=sina1*math.cos(a2)
            py=sina1*math.sin(a2)
            pz=math.cos(a1)
            a3=90.0*d-rotlat*d
            sina3=math.sin(a3)
            a4=rotan*d
            cosa4=math.cos(a4)
            sina4=math.sin(a4)
            a5=rotlo*d
            sina5=math.sin(a5)
            cosa5=math.cos(a5)
            gx=sina3*cosa5
            gy=sina3*sina5
            gz=math.cos(a3)
            vct=(px*gx)+(py*gy)+(pz*gz)
            rx=cosa4*px+(1.0-cosa4)*vct*gx+sina4*(gy*pz-gz*py)
            ry=cosa4*py+(1.0-cosa4)*vct*gy+sina4*(gz*px-gx*pz)
            rz=cosa4*pz+(1.0-cosa4)*vct*gz+sina4*(gx*py-gy*px)

            if (rz == 1.0):
                acos1 = 0.0
            
            if (rz != 1.0):
                asin1=math.atan(rz/math.sqrt(1.0-(rz*rz)))
                acos1=(((3.14159/2.0)-asin1)*57.29578)

            anlat=90.0-acos1
            anlong=90.0-(math.atan2(rx,ry)*57.29578)
            if (anlong > 180.0):
                anlong=anlong-360.0
        
        return anlong, anlat