import pygplates
import csv

def make_feature_collection(dat_file):
    feature_collection = []
    with open(dat_file, 'r') as f:
        while True:
            h1 = f.readline()
            if not h1: break
            h2 = f.readline().split()
            plateid = int(h2[0])
            feature = pygplates.Feature(pygplates.FeatureType.gpml_unclassified_feature)
            feature.add(pygplates.PropertyName.gpml_reconstruction_plate_id, 
                        pygplates.GpmlConstantValue(pygplates.GpmlPlateId(plateid)))
            geo_points = []
                
            while True:
                record = f.readline().split()
                lat = float(record[0])
                lon = float(record[1])
                                
                if lat >= 99:
                    if len(geo_points) == 0: break
                    geo = pygplates.PolygonOnSphere(geo_points)
                    feature.set_geometry(geo)
                    feature_collection.append(feature)
                    break

                geo_points.append((lat, lon))
    
    return pygplates.FeatureCollection(feature_collection)

def assign_plate_ids(static_polygons_filename, rot_file, csv_data_file):
    
    # Load one or more rotation files into a rotation model.
    rotation_model = pygplates.RotationModel(rot_file)

    input_points = []
    with open(csv_data_file, "r") as infile:
        infile.readline() # throw away header
        line = infile.readline()
        while line:
            datapoint = line.split(",")
            lat = float(datapoint[3])
            lon = float(datapoint[4])

            # Create a pyGPlates point from the latitude and longitude, and add it to our list of points.
            # Note that pyGPlates uses the opposite (lat/lon) order to GMT (lon/lat).
            input_points.append(pygplates.PointOnSphere(lat, lon))

            line = infile.readline()

    # Create a feature for each point we read from the input file.
    point_features = []
    for i, point in enumerate(input_points):

        # Create an unclassified feature.
        point_feature = pygplates.Feature()

        # Set the feature's geometry to the input point read from the text file.
        point_feature.set_geometry(point)
        point_feature.set_name(str(i + 1))

        point_features.append(point_feature)

    # Use the static polygons to assign plate IDs and valid time periods.
    # Each point feature is partitioned into one of the static polygons and assigned its
    # reconstruction plate ID and valid time period.
    # partitioned_features, unpartitioned_features = pygplates.partition_into_plates(
    #     static_polygons_filename,
    #     rotation_model,
    #     point_features,
    #     properties_to_copy = [
    #         pygplates.PartitionProperty.reconstruction_plate_id,
    #         pygplates.PartitionProperty.valid_time_period],
    #     partition_return = pygplates.PartitionReturn.separate_partitioned_and_unpartitioned)
    
        # If the given file results in no partitioned data, try to modify the file so that
    # it reconstructs as polygons
    
    # if len(partitioned_features) == 0:
    # print('repartitioning')
    # plate_collection = []
    # feature_plates = []
    # pygplates.reconstruct(static_polygons_filename, rotation_model, plate_collection, 0)
    # for plate in plate_collection:
    #     if plate.get_reconstructed_geometry() is not pygplates.PolygonOnSphere:
    #         try:
    #             print('fixing polygon')
    #             geo = pygplates.PolygonOnSphere(plate.get_reconstructed_geometry())
    #             feature = pygplates.Feature(pygplates.FeatureType.gpml_unclassified_feature)
    #             feature.set_geometry(geo)
    #             feature_plates.append(feature)
    #         except Exception as e:
    #             print(f"{type(e).__name__}: {e}")
    #             print(plate.get_reconstructed_geometry())
    #             del(plate)
    #             continue
    # feature_collection = pygplates.FeatureCollection(feature_plates)
    file_extension = static_polygons_filename[-4:].lower()
    if file_extension == ".dat":
        static_polygons = make_feature_collection(static_polygons_filename)
    else:
        static_polygons = static_polygons_filename

    partitioned_features, unpartitioned_features = pygplates.partition_into_plates(
        static_polygons,
        rotation_model,
        point_features,
        properties_to_copy = [
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period],
        partition_return = pygplates.PartitionReturn.separate_partitioned_and_unpartitioned)

    print(f"Partitioned: {len(partitioned_features)}, Unpartitioned: {len(unpartitioned_features)}")

    if unpartitioned_features:
        print(f"Warning: {len(unpartitioned_features)} were not partitioned")
        for point in unpartitioned_features:
            lat, lon = point.get_geometry().to_lat_lon_list()[0]
            plateid = point.get_reconstruction_plate_id()
            print(f"    Point at {lat}, {lon}, id: {plateid}")

    with open(csv_data_file, mode='r', newline='\n') as infile:
        rows = list(csv.reader(infile))  # Read all rows into a list

    for feature in partitioned_features:

        # the name for each feature was set as the row it came from
        row_num = int(feature.get_name())

        # enters the plate id into the plate id column for that row
        rows[row_num][2] = feature.get_reconstruction_plate_id()

        start, end = feature.get_valid_time()

        # if data point started before plate, set start to plate
        if start < float(rows[row_num][8]):
            rows[row_num][8] = str(start)

        # if data point ended after plate, set end to plate
        if end > float(rows[row_num][9]):
            rows[row_num][9] = str(end)

    new_file = csv_data_file[:-4] + "_wplateid.csv"
    with open(new_file, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)


    return new_file




