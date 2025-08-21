import numpy as np
import math

from file_handling import Record

class RotationEngine:

    def __init__(self, max_num_plates=500):
        # Constants
        self.DEG_TO_RAD = 180.0 / math.pi
        self.PI_OVER_2 = math.pi / 2.0
        self.d = .017453292519943
        
        # Initialize arrays with proper dimensions
        self.max_num_plates = max_num_plates
        self.reset_arrays()
        
    def reset_arrays(self):
        # stores unflattened rotation data at index
        self.rotation_data = np.zeros((self.max_num_plates, 4))
        # stores plate id and refplate at index
        self.rotation_metadata = np.zeros((self.max_num_plates, 3), dtype=int)
        # stores flattened rotation data at index
        self.final_rotation_data = np.zeros((self.max_num_plates, 4))
        
        # k: plateid; v: index
        self.plate_id_to_index = {}
        # k: refplate; v: index
        self.rotation_index_map = {}
        # stores plateid at index
        self.rot_list = np.zeros(self.max_num_plates, dtype=np.int16)

    def resize_arrays(self):
        self.rotation_data = np.pad(self.rotation_data, ((0, self.max_num_plates), (0, 0)))
        self.rotation_metadata = np.pad(self.rotation_metadata, ((0, self.max_num_plates), (0, 0)))
        self.final_rotation_data = np.pad(self.final_rotation_data, ((0, self.max_num_plates), (0, 0)))
        self.rot_list = np.pad(self.rot_list, (0, self.max_num_plates))

        # print(f"rotation_data: {self.rotation_data.shape}")
        # print(f"rotation_metadata: {self.rotation_metadata.shape}")
        # print(f"final_rotation_data: {self.final_rotation_data.shape}")
        # print(f"rot_list: {self.rot_list.shape}")

        self.max_num_plates *= 2
        
    def rotfnd(self, rotation_filename, target_time):

        # Initialize variables
        current_time = 0.0
        current_pole_lat = 0.0
        current_pole_lon = 0.0
        current_rotation_angle = 0.0
        previous_time = 0.0
        previous_pole_lat = 0.0
        previous_pole_lon = 0.0
        previous_rotation_angle = 0.0
        interpolated_pole_lat = 0.0
        interpolated_pole_lon = 0.0
        interpolated_angle = 0.0
        
        rotation_counter = 0
        output_index = 0
        current_plate_id = 0
        previous_plate_id = 9999
        current_ref_frame = 0
        previous_ref_frame = 0

        with open(rotation_filename, "r") as rotation_file:
            processing_plate = True
            
            # --- PHASE 1: Time Interpolation ---
            while processing_plate:
                valid_time_range = True
                while valid_time_range:
                    if current_plate_id != 999:  # 999 indicates invalid record
                        previous_plate_id = current_plate_id
                        previous_time = current_time
                        previous_pole_lat = current_pole_lat
                        previous_pole_lon = current_pole_lon
                        previous_rotation_angle = current_rotation_angle
                        previous_ref_frame = current_ref_frame

                    # Read until valid plate ID found
                    while True:
                        line = rotation_file.readline()
                        if not line:
                            print("Reached end of rotation file")
                            raise EOFError("Reached end of rotation file before " \
                            "finding all valid rotations: lower plot time or load new rotation file")

                        record = line.split()
                        current_plate_id = int(record[0])
                        
                        if current_plate_id != 999:  # Valid plate
                            current_time = float(record[1])
                            current_pole_lat = float(record[2])
                            current_pole_lon = float(record[3])
                            current_rotation_angle = float(record[4])
                            current_ref_frame = int(record[5])
                            break

                    if target_time <= current_time and previous_plate_id == current_plate_id:
                        valid_time_range = False

                # Check reference frame consistency
                if previous_ref_frame != current_ref_frame:
                    print(f"Reference frame mismatch found in .rot file between the following lines:\n \
                                     {previous_plate_id} {previous_time} ... {previous_ref_frame}\n \
                                     {current_plate_id} {current_time} ... {current_ref_frame}")
                    continue
                    raise ValueError(f"Reference frame mismatch found in .rot file between the following lines:\n \
                                     {previous_plate_id} {previous_time} ... {previous_ref_frame}\n \
                                     {current_plate_id} {current_time} ... {current_ref_frame}")

                # Linear interpolation in time
                if current_time - previous_time == 0 and current_time == 0:
                    time_weight = 0
                else:
                    time_weight = (current_time - target_time) / (current_time - previous_time)
                
                try: 
                    # First rotation combination
                    temp_angle = -current_rotation_angle
                    combined = self.adder(
                        current_pole_lat, current_pole_lon, temp_angle,
                        previous_pole_lat, previous_pole_lon, previous_rotation_angle)
                    interpolated_pole_lat, interpolated_pole_lon, interpolated_angle = combined
                    interpolated_angle *= time_weight

                    # Second combination
                    combined = self.adder(
                        current_pole_lat, current_pole_lon, current_rotation_angle,
                        interpolated_pole_lat, interpolated_pole_lon, interpolated_angle)
                    interpolated_pole_lat, interpolated_pole_lon, interpolated_angle = combined
                except Exception as e:
                    print(f"current plate id: {current_plate_id}\n current time: {current_time}\n" \
                          f"current pole lat: {current_pole_lat}\n " \
                        f"current pole lon: {current_pole_lon}\n " \
                        f"current rotation angle: {current_rotation_angle}")
                    raise e

                # Store results
                rotation_counter += 1

                if rotation_counter >= self.max_num_plates:
                    self.resize_arrays()

                self.rotation_data[rotation_counter][1] = interpolated_pole_lat
                self.rotation_data[rotation_counter][2] = interpolated_pole_lon
                self.rotation_data[rotation_counter][3] = interpolated_angle
                self.rotation_metadata[rotation_counter][1] = previous_ref_frame
                self.rotation_metadata[rotation_counter][2] = previous_plate_id
                self.rotation_index_map[previous_plate_id] = rotation_counter

                # Read until plate ID changes
                while True:
                    line = rotation_file.readline()
                    if not line:
                        print("File processing complete, building reconstruction")
                        break

                    record = line.split()
                    current_plate_id = int(record[0])
                    current_time = float(record[1])
                    current_pole_lat = float(record[2])
                    current_pole_lon = float(record[3])
                    current_rotation_angle = float(record[4])
                    current_ref_frame = int(record[5])

                    if current_plate_id != 999 and current_plate_id != previous_plate_id:
                        break

                if current_plate_id == previous_plate_id:
                    processing_plate = False

            # --- PHASE 2: Reference Frame Reduction ---
            while output_index <= rotation_counter:
                # Current rotation parameters
                pole_lat = self.rotation_data[output_index][1]
                pole_lon = self.rotation_data[output_index][2]
                rotation_angle = self.rotation_data[output_index][3]
                ref_frame = self.rotation_metadata[output_index][1]

                if ref_frame == 0:  # Absolute rotation
                    self.rotation_metadata[output_index][1] = 0
                    interpolated_pole_lat = pole_lat
                    interpolated_pole_lon = pole_lon
                    interpolated_angle = rotation_angle
                else:
                    # Hierarchical reduction through reference frames
                    try:
                        ref_index = self.rotation_index_map[ref_frame]
                        ref_pole_lat = self.rotation_data[ref_index][1]
                        ref_pole_lon = self.rotation_data[ref_index][2]
                        ref_angle = self.rotation_data[ref_index][3]
                    except KeyError:
                        raise ValueError(f"Plate {ref_frame} is being used as a reference plate for Plate \
                                          {self.rotation_metadata[output_index][2]} for target time {target_time} \
                                            but does not yet exist. Please fix rotation file.")

                    while True:
                        combined = self.adder(
                            pole_lat, pole_lon, rotation_angle,
                            ref_pole_lat, ref_pole_lon, ref_angle)
                        interpolated_pole_lat, interpolated_pole_lon, interpolated_angle = combined

                        ref_frame = self.rotation_metadata[ref_index][1]
                        if ref_frame == 0:
                            self.rotation_data[output_index][1] = interpolated_pole_lat
                            self.rotation_data[output_index][2] = interpolated_pole_lon
                            self.rotation_data[output_index][3] = interpolated_angle
                            self.rotation_metadata[output_index][1] = 0
                            break
                        else:
                            ref_index = self.rotation_index_map[ref_frame]
                            pole_lat, pole_lon, rotation_angle = interpolated_pole_lat, interpolated_pole_lon, interpolated_angle
                            ref_pole_lat = self.rotation_data[ref_index][1]
                            ref_pole_lon = self.rotation_data[ref_index][2]
                            ref_angle = self.rotation_data[ref_index][3]

                # Store final output
                self.rot_list[output_index] = self.rotation_metadata[output_index][2]
                self.final_rotation_data[output_index][1] = interpolated_pole_lat
                self.final_rotation_data[output_index][2] = interpolated_pole_lon
                self.final_rotation_data[output_index][3] = interpolated_angle
                self.plate_id_to_index[self.rotation_metadata[output_index][2]] = output_index

                output_index += 1

        with open("rotfnd_output.txt", 'w') as outfile:
            for plateid, index in self.plate_id_to_index.items():
                if index == -1:
                    continue
                plateid2 = self.rotation_metadata[index][2]
                plat = round(self.final_rotation_data[index][1], 2)
                plon = round(self.final_rotation_data[index][2], 2)
                pang = round(self.final_rotation_data[index][3], 2)
                refplate = self.rotation_metadata[index][1]

                outfile.write(f"plateid: {plateid} {plateid2}, plat: {plat}, plon: {plon}, pang: {pang}, refplate: {refplate}\n")
            

    def adder(self, pole1_lat, pole1_lon, angle1, pole2_lat, pole2_lon, angle2):
        # Edge cases
        if angle1 == -angle2:
            return 90.0, 0.0, 0.0
        if angle1 == 0.0:
            return pole2_lat, pole2_lon, angle2
        if angle2 == 0.0:
            return pole1_lat, pole1_lon, angle1

        # Convert to radians
        lat1_rad = pole1_lat / self.DEG_TO_RAD
        lon1_rad = pole1_lon / self.DEG_TO_RAD
        angle1_rad = angle1 / self.DEG_TO_RAD
        lat2_rad = pole2_lat / self.DEG_TO_RAD
        lon2_rad = pole2_lon / self.DEG_TO_RAD
        angle2_rad = angle2 / self.DEG_TO_RAD

        # Quaternion components for rotation 1
        q1_w = math.cos(angle1_rad / 2.0)
        q1_x = math.sin(angle1_rad / 2.0) * math.sin(self.PI_OVER_2 - lat1_rad) * math.cos(lon1_rad)
        q1_y = math.sin(angle1_rad / 2.0) * math.sin(self.PI_OVER_2 - lat1_rad) * math.sin(lon1_rad)
        q1_z = math.sin(angle1_rad / 2.0) * math.cos(self.PI_OVER_2 - lat1_rad)

        # Quaternion components for rotation 2
        q2_w = math.cos(angle2_rad / 2.0)
        q2_x = math.sin(angle2_rad / 2.0) * math.sin(self.PI_OVER_2 - lat2_rad) * math.cos(lon2_rad)
        q2_y = math.sin(angle2_rad / 2.0) * math.sin(self.PI_OVER_2 - lat2_rad) * math.sin(lon2_rad)
        q2_z = math.sin(angle2_rad / 2.0) * math.cos(self.PI_OVER_2 - lat2_rad)

        # Hamilton product (quaternion multiplication)
        combined_w = q1_w*q2_w - q1_x*q2_x - q1_y*q2_y - q1_z*q2_z
        combined_x = q1_w*q2_x + q1_x*q2_w - q1_y*q2_z + q1_z*q2_y
        combined_y = q1_w*q2_y + q1_x*q2_z + q1_y*q2_w - q1_z*q2_x
        combined_z = q1_w*q2_z - q1_x*q2_y + q1_y*q2_x + q1_z*q2_w

        # Convert back to Euler pole
        total_angle = math.acos(combined_w) * 2.0 * self.DEG_TO_RAD
        if total_angle == 0.0:
            return 90.0, 0.0, 0.0
        if total_angle > 180.0:
            total_angle -= 360.0

        # Calculate pole position
        try:
            pole_lat = 90.0 - math.acos(combined_z / math.sin(total_angle / (2 * self.DEG_TO_RAD))) * self.DEG_TO_RAD
        except ZeroDivisionError:
            return 90.0, 0.0, 0.0

        if total_angle < 0.0:
            pole_lat = -pole_lat

        pole_lon = math.atan2(combined_y, combined_x) * self.DEG_TO_RAD
        if pole_lon > 180.0:
            pole_lon -= 360.0

        return pole_lat, pole_lon, total_angle
    
    def rotate(self, alat,along,rotlat,rotlo, rotan):

        if (alat == 90.0):
                alat=89.9     #/* handle the exceptions */
        if (alat == -90.0):
                alat=-89.9

        if (rotan == 0.0):
            anlat = alat
            anlong = along

        if (rotan != 0.0):
            a1=90.0*self.d-alat*self.d
            sina1=math.sin(a1)
            a2=along*self.d
            px=sina1*math.cos(a2)
            py=sina1*math.sin(a2)
            pz=math.cos(a1)
            a3=90.0*self.d-rotlat*self.d
            sina3=math.sin(a3)
            a4=rotan*self.d
            cosa4=math.cos(a4)
            sina4=math.sin(a4)
            a5=rotlo*self.d
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
        
        return anlat, anlong
    
    def process_chunks(self, chunk_generator):

        for chunk in chunk_generator:
            plateid = int(chunk.plateid)  # Extract plateid from second header
            if plateid in self.plate_id_to_index:
                int_rot = self.plate_id_to_index[plateid]
                rotlat = self.final_rotation_data[int_rot][1]
                rotlo = self.final_rotation_data[int_rot][2]
                rotan = self.final_rotation_data[int_rot][3]
            else:
                print(f"Plate id {plateid} not in rotation file. Assigning zero rotation")
                rotlat = 0.0
                rotlo = 0.0
                rotan = 0.0

            # Modify records in the chunk
            modified_records = []
            for record in chunk.records:
                pre_lat = record.alat
                pre_long = record.along
                pen = record.pen
                
                post_lat, post_long = self.rotate(pre_lat, pre_long, rotlat, rotlo, rotan)                
                modified_records.append(Record(round(post_lat, 4), round(post_long, 4), pen))

            # first_long = round(modified_records[0]["along"], 4)
            # first_lat = round(modified_records[0]["alat"], 4)
            # last_long = round(modified_records[-1]["along"], 4)
            # last_lat = round(modified_records[-1]["alat"], 4)
            # num = len(modified_records)
            # if last_long - first_long > 0.1:
            #     print(f"rot  open  : ({first_long}, {first_lat}) ({last_long}, {last_lat}), {num}")
            # else:
            #     print(f"rot  closed: ({first_long}, {first_lat}) ({last_long}, {last_lat}), {num}")

            chunk.records = modified_records
            yield chunk

    def hold_fixed_option(self, fixed_id):
        # need to check variables to see if any are global variables

        rlat = 0.0
        rlon = 0.0
        rang = 0.0

        i = int(self.plate_id_to_index[fixed_id])
        print("hold fixed value for i = ", i)
        rotlat1 = self.rotation_data[i][1]
        rotlo1 = self.rotation_data[i][2]
        rotan1 = -self.rotation_data[i][3]
        print("rotlat1, rotlo1, rotan1 = ", rotlat1, rotlo1, rotan1)

        for i in range(0, 2000):

            id = self.rot_list[i]
            plat = self.rotation_data[i][1]
            plon = self.rotation_data[i][2]
            pang = self.rotation_data[i][3]
            if ((id == 0) and (i > 1)):
                break
            if (pang != 0.0):
                qlat = rotlat1
                qlon = rotlo1
                qang = rotan1
        
                rlat, rlon, rang = self.adder(plat, plon, pang, qlat, qlon, qang)

                self.final_rotation_data[i][1] = rlat
                self.final_rotation_data[i][2] = rlon
                self.final_rotation_data[i][3] = rang
            i = i + 1

# rot = RotationEngine()
# rot.rotfnd("Scotese_forPgeog_v19o_r1c_fixed.rot", 250)