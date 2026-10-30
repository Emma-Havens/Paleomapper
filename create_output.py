import pygplates
import os

class saveFile:

    def __init__(self, output_file, desired_extension, is_animation):
        self.desired_extension = desired_extension
        extless_path = os.path.splitext(output_file)[0]
        self.file_base = os.path.basename(extless_path)
        self.folder_path = os.path.dirname(extless_path)
        self.output_file = extless_path + self.desired_extension
        self.is_animation = is_animation
        self.file_counter = 0
        self.saved_files = []

    def get_output_path(self):
        if self.is_animation:
            tmp_basename = "." + self.file_base + str(self.file_counter) + self.desired_extension
            output_path = os.path.join(self.folder_path, tmp_basename)
            self.file_counter += 1
            self.saved_files.append(output_path)
            return output_path
        else:
            return self.output_file
        
    
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
            
            # if not chunk.appears >= 999.0:
            chunk.appears = chunk.appears - plot_time
            # if not chunk.disappears <= -999.0:
            chunk.disappears = chunk.disappears - plot_time
            valid_time = (chunk.appears, chunk.disappears)
            feature_type = self.assign_feature_type(chunk.feature_type)
            recon_plateid = chunk.plateid
            conj_plateid = chunk.plateid2
            name = chunk.label

            if chunk.symbol == "dot":
                point = pygplates.PointOnSphere(chunk.records[0].alat, chunk.records[0].along)
                feature = pygplates.Feature.create_reconstructable_feature(feature_type, point, name=name, 
                                                                                    valid_time=valid_time, 
                                                                                    reconstruction_plate_id=recon_plateid,
                                                                                    conjugate_plate_id=conj_plateid)
                features.append(feature)
            
            else:
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
            feature_collection.write(self.get_output_path())

    def assemble_animation(self):
        if not self.is_animation: return
        feature_collections = []
        for file in self.saved_files:
            feature_collection = pygplates.FeatureCollection(file)
            feature_collections.extend(feature_collection)
            os.remove(file)
        merged_collection = pygplates.FeatureCollection(feature_collections)
        merged_collection.write(self.output_file)