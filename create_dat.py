

class saveDAT:

    def __init__(self, dat_file):
        file_extension = dat_file[-4:]
        if file_extension == ".dat":
            self.dat_file = dat_file
        else:
            self.dat_file = dat_file + ".dat"

    def save_to_dat(self, chunk_generator, plot_time):
        with open(self.dat_file, "w") as f:
            for chunk in chunk_generator:

                data_type = chunk.data_type
                plateid = chunk.plateid
                appears = chunk.appears
                disappears = chunk.disappears
                id_type = chunk.feature_type
                id_type_mod = chunk.feature_type_mod
                plateid2 = chunk.plateid2
                color_placeholder = 0
                record_number = chunk.record_number

                label = chunk.label
                bcolor = chunk.border_color
                fcolor = chunk.fill_color
                symbol = chunk.symbol
                size = chunk.size
                azimuth = chunk.azimuth
                
                # Adjust appears and disappears based on plot_time
                if not appears >= 999.0:
                    appears = appears - plot_time
                if not disappears <= -999.0:
                    disappears = max(disappears - plot_time, -999.0)

                # Write the first header line
                f.write(f"9999 9999,{data_type},{label},{symbol},{bcolor},{fcolor},{size},{azimuth}\n")
                
                # Write the modified second header line
                # f.write(f"{plateid} {appears} {disappears} {id_type} {plateid2} {color} {extra}\n")
                f.write('%4d%7.1f%7.1f%3s%4d%4d%4d%6d\n' % (plateid,appears,disappears,id_type,id_type_mod,plateid2,color_placeholder,record_number))
                
                # Write records
                for record in chunk.records:
                    alat = record.alat
                    along = record.along
                    pen = record.pen
                    # f.write(f"  {alat} {along} {pen}\n")
                    f.write('%9.4f%10.4f%2d\n' % (float(alat), float(along), int(pen)))

                # write end line
                f.write("  99.0000   99.0000 3\n")

                yield chunk