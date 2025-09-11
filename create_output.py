import pygplates
import os

class saveFile:

    def __init__(self, output_file, desired_extension):
        file_base = os.path.splitext(output_file)[0]
        self.output_file = file_base + desired_extension

    def assign_feature_type(self, gpml_feature):
        match gpml_feature:
            case "SS":
                return pygplates.FeatureType.gpml_mid_ocean_ridge
            case "CS":
                return pygplates.FeatureType.gpml_passive_continental_boundary
            case "RI":
                return pygplates.FeatureType.gpml_continental_rift
            case "CM":
                return pygplates.FeatureType.gpml_extended_continental_crust
            case "SU":
                return pygplates.FeatureType.gpml_subduction_zone
            case "TH":
                return pygplates.FeatureType.gpml_transform
            case "IS":
                return pygplates.FeatureType.gpml_island_arc
            case _:
                return pygplates.FeatureType.gpml_unclassified_feature
    
    def save_to_file(self, chunk_generator, plot_time):
        features = []
        for chunk in chunk_generator:
            
            if not chunk.appears >= 999.0:
                chunk.appears = chunk.appears - plot_time
            if not chunk.disappears <= -999.0:
                chunk.disappears = max(chunk.disappears - plot_time, -999.0)
            valid_time = (chunk.appears, chunk.disappears)
            feature_type = self.assign_feature_type(chunk.feature_type)
            recon_plateid = chunk.plateid
            conj_plateid = chunk.plateid2
            name = chunk.label
            
            geometry = None
            points = []
            for record in chunk.records:
                points.append(pygplates.PointOnSphere(record.alat, record.along))
            if points and points[0] == points[-1]:
                geometry = pygplates.PolygonOnSphere(points)
            elif points:
                geometry = pygplates.PolylineOnSphere(points)
            
            if geometry:
                
                feature = pygplates.Feature.create_reconstructable_feature(feature_type, geometry, name=name, 
                                                                   valid_time=valid_time, 
                                                                   reconstruction_plate_id=recon_plateid,
                                                                   conjugate_plate_id=conj_plateid)
                features.append(feature)

            yield chunk

        if features:
            feature_collection = pygplates.FeatureCollection(features)
            feature_collection.write(self.output_file)