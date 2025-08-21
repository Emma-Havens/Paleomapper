import csv
import os
os.environ["QT_API"] = "pyside6"
import pygplates
import os.path
import sys
from matplotlib.colors import is_color_like
from dataclasses import dataclass
from typing import List

import symbols

@dataclass
class Record:
    alat: float
    along: float
    pen: int

@dataclass
class Chunk:
    data_type: str
    plateid: int
    appears: float
    disappears: float
    feature_type: str
    feature_type_mod: int
    plateid2: int
    border_color: str
    fill_color: str
    record_number: int
    label: str
    symbol: str
    size: float
    azimuth: float
    records: List[Record]

def read_csv_in_chunks(csv_file, plot_time, bcolor, fcolor):

    # load symbols in memory
    shape_library = "shape_library.csv"
    if getattr(sys, 'frozen', False):
        bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        shape_library = bundle_dir + "/" + shape_library
        print(shape_library)
    symbols.load_shape_library(shape_library)

    with open(csv_file, "r") as infile:
        reader = csv.reader(infile)
        next(reader)    # throw away header
        for line in enumerate(reader):
            row = line[1]  # extract row data

            start_time = float(row[8])
            end_time = float(row[9])
            if not ((start_time >= plot_time or start_time >= 999) and (end_time <= plot_time or end_time <= -999)):
                continue

            file_type = "CSV"
            urn = int(row[0])
            label = row[1]
            plateid = int(row[2])
            lat = float(row[3])
            lon = float(row[4])
            symbol = row[5]
            size = float(row[6])
            azimuth = float(row[7])
            border_color = row[10]
            fill_color = row[11]

            if bcolor: border_color = bcolor
            if fcolor: fill_color = fcolor

            chunk = Chunk(file_type, plateid, start_time, end_time, "DP", 0, plateid, 
                          border_color, fill_color, urn, label, symbol, size, azimuth, [])
            
            match symbol:
                case "circle":
                    path = symbols.create_circle(lat, lon, size)
                case "dot":
                    path = symbols.create_circle(lat, lon, 0.1)
                case "urn":
                    path = symbols.create_text(lat, lon, size, azimuth, str(urn))
                case "label":
                    path = symbols.create_text(lat, lon, size, azimuth, label)
                case _:
                    path = symbols.create_symbol(lat, lon, size, azimuth, symbol)
            
            for i in range(len(path.vertices)):
                point = path.vertices[i]
                code = path.codes[i]
                if code in [0, 79]: # legacy ignored codes
                    continue
                elif code == 1:     # MOVETO
                    pen = 3
                else:               # LINETO, CURVE3, CURVE4
                    pen = 2
            
                chunk.records.append(Record(point[1], point[0], pen))
    
            yield chunk

def sanitize_dat(filename, plot_time):

    in_file = open(filename,"r")
    geo_reduced_outfile = "plate_reduced.dat"
    out_file = open(geo_reduced_outfile, "w")

    young_time = plot_time
    old_time = plot_time
    
    geographic_records_to_read = True
    while geographic_records_to_read == True:
        header1 = in_file.readline()   #1st plate_id header line
        if (header1 == ""):
            print ("File Finished")
            break
        
        parser = in_file.readline()  # 2nd line of plate_id header
        if parser == "":
            break
#        
        record_list = parser.split()
        appears = float(record_list[1])
        disappears = float(record_list[2])

        if (((appears >= young_time) and (disappears <= old_time)) or ((appears >= 999.0) and (disappears <= -999.0))):
            valid_time = True
            while valid_time == True:
                out_file.write(header1)
                out_file.write(parser)
                valid_record = True
                while valid_record == True:
                    parser = in_file.readline()
                    out_file.write(parser)
                    record_list = parser.split()
                    latpoint_int = int(float(record_list[0]))
                    if latpoint_int >= 99:
                        valid_record = False
                        valid_time = False

        else:
            valid_time = False
            while valid_time == False:
                parser = in_file.readline()
                record_list = parser.split()
                latpoint_int = int(float(record_list[0]))
                if latpoint_int >= 99:
                    valid_time = True

    out_file.close()

    return geo_reduced_outfile


def read_file_in_chunks(filename, bcolor, fcolor):
    """
    Generator that reads the file in plate sized chunks, yielding one chunk at a time.
    """
    with open(filename, "r") as infile:
        while True:           
            # Read the first header
            header1 = infile.readline()
            if not header1:
                break  # End of file
            h1 = header1.split(",")

            if len(h1) == 8:
                label = h1[2]
                symbol = h1[3] if h1[3] in symbols.Shapes else "none"
                if is_color_like(h1[4]):
                    border_color = h1[4]
                elif h1[4] == "multicolor":
                    border_color = "multicolor"
                else:
                    border_color = "black"
                if is_color_like(h1[5]):
                    fill_color = h1[5]
                elif h1[5] == "multicolor":
                    fill_color = "multicolor"
                else:
                    fill_color = "none"
                try: 
                    size = float(h1[6])
                except ValueError: 
                    size = 1
                try:
                    azimuth = float(h1[7])
                except ValueError:
                    azimuth = 0
            else:
                label = "nolabel"
                symbol = "none"
                border_color = "black"
                fill_color = "none"
                size = 1
                azimuth = 0
            
            # Read the second header
            header2 = infile.readline()
            if not header2:
                break  # End of file
            h2 = header2.split()
            
            file_type = "DAT"
            plateid = int(h2[0])
            appears = float(h2[1])
            disappears = float(h2[2])
            feature_type = h2[3]
            feature_type_mod = int(h2[4])
            plateid2 = int(h2[5])
            record_number = int(h2[7])

            if bcolor: border_color = bcolor
            if fcolor: fill_color = fcolor

            # print(f"{label}: {border_color}, {fill_color}")
            
            chunk = Chunk(file_type, plateid, appears, disappears, feature_type, feature_type_mod, plateid2, 
                          border_color, fill_color, record_number, label, symbol, size, azimuth, [])

            
            # Read records until end of section (alat = 99)
            while True:
                record_line = infile.readline()                
                record_list = record_line.split()
                
                alat = float(record_list[0])
                along = float(record_list[1])
                pen = int(record_list[2])
                
                if alat >= 99.0:  # End of section
                    break
                
                chunk.records.append(Record(alat, along, pen))
            
            yield chunk

def assign_feature_type(gpml_feature):
    match gpml_feature:
        case pygplates.FeatureType.gpml_mid_ocean_ridge:
            return "SS"
        case pygplates.FeatureType.gpml_passive_continental_boundary:
            return "CS"
        case pygplates.FeatureType.gpml_continental_rift:
            return "RI"
        case pygplates.FeatureType.gpml_extended_continental_crust:
            return "CM"
        case pygplates.FeatureType.gpml_subduction_zone:
            return "SU"
        case pygplates.FeatureType.gpml_transform:
            return "TH"
        case pygplates.FeatureType.gpml_island_arc:
            return "IS"
        case _:
            return "UN" # Put GN somewhere

def read_gpml_in_chunks(filename, plot_time, bcolor, fcolor):

    col = pygplates.FeatureCollection(filename)

    for feature in col:

        file_type = "GPML"
        plateid = int(feature.get_reconstruction_plate_id())
        valid_time = feature.get_valid_time()
        appears = valid_time[0] if valid_time else 0.0
        disappears = valid_time[1] if valid_time else 0.0
        feature_type = assign_feature_type(feature.get_feature_type())
        plateid2 = int(feature.get_conjugate_plate_id())
        # record_number = int(feature.get_feature_id())

        if not ((appears >= plot_time or appears >= 999) and (disappears <= plot_time or disappears <= -999)):
            continue

        chunk = {"data_type": file_type, 
                     "headers": {"plateid": plateid, "appears": appears, "disappears": disappears, 
                                 "feature_type": feature_type, "feature_type_mod": 0, 
                                 "plateid2": plateid2, "border_color": bcolor, "fill_color": fcolor, "record_number": 0},
                     "records": []}
        
        chunk = Chunk(file_type, plateid, appears, disappears, feature_type, 0, plateid2, 
                          bcolor, fcolor, 0, "nolabel", "none", 1, 0, [])

        geometry = feature.get_geometries()
        if geometry:
            for segment in geometry:
                chunk.records = []
                points = list(segment.to_lat_lon_list())
                if type(segment) is pygplates.PolygonOnSphere:
                    points.append(points[0])
                # else:
                #     print(f"{type(segment)} detected: {points[0][0]} {points[0][1]}")
                chunk.records.append(Record(points[0][0], points[0][1], 3))
                for lat, lon in points[1:]:
                    chunk.records.append(Record(lat, lon, 2))
        
                # first_long = round(chunk["records"][0]["along"], 4)
                # first_lat = round(chunk["records"][0]["alat"], 4)
                # last_long = round(chunk["records"][-1]["along"], 4)
                # last_lat = round(chunk["records"][-1]["alat"], 4)
                # num = len(chunk["records"])
                # if abs(last_long - first_long) > 0.1:
                #     print(f"file open  : ({first_long}, {first_lat}) ({last_long}, {last_lat}), {num}")
                # else:
                #     print(f"file closed: ({first_long}, {first_lat}) ({last_long}, {last_lat}), {num}")

                yield chunk

def read_files(files, plot_time):
    for total_file in files:
        _, _, file, border_color, fill_color = total_file
        if border_color == "infile": border_color = ""
        if fill_color == "infile": fill_color = ""
        extension = os.path.splitext(file)[1]
        match extension:
            case ".csv":
                for chunk in read_csv_in_chunks(file, plot_time, border_color, fill_color):
                    yield chunk
            case ".dat":
                dat = sanitize_dat(file, plot_time)
                for chunk in read_file_in_chunks(dat, border_color, fill_color):
                    yield chunk
            case ".gpml":
                for chunk in read_gpml_in_chunks(file, plot_time, border_color, fill_color):
                    yield chunk