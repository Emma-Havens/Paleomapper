import csv
import symbols


def dat_to_csv(dat_file, csv_file):
    infile = open(dat_file, "r")
    outfile = open(csv_file, "w")
    writer = csv.writer(outfile)
    writer.writerow(["URN", "label", "PlateID", "Latitude", "Longitude", "Symbol", "Size", 
                                "Azimuth", "Start", "End", "Border color", "Fill color"])
    while True:           
        # Read the first header
        header1 = infile.readline()
        if not header1:
            break  # End of file
        h1 = header1.split(",")

        if len(h1) == 8:
            label = h1[2]
            symbol = h1[3] if h1[3] in symbols.Shapes else "none"
            border_color = h1[4]
            fill_color = h1[5]
            try: 
                size = float(h1[6])
            except ValueError: 
                size = 1
            try:
                azimuth = float(h1[7])
            except ValueError:
                azimuth = 0
        else:
            print("dat is not convertable")
            return
        
        # Read the second header
        header2 = infile.readline()
        if not header2:
            break  # End of file
        h2 = header2.strip().split()
        
        plateid = int(h2[0])
        appears = float(h2[1])
        disappears = float(h2[2])
        urn = int(h2[7])
        
        # Read records until end of section (alat = 99)
        while True:
            record_line = infile.readline()                
            record_list = record_line.split()

            if float(record_list[0]) >= 99.0:  # End of section
                break
            
            lat = float(record_list[0])
            lon = float(record_list[1])

        writer.writerow([urn, label, plateid, round(lat, 2), round(lon, 2), symbol, size, azimuth, appears, disappears, border_color, fill_color])


dat_name = "working/300Ma_citydots.dat"
csv_name = "working/300Ma_citydots.csv"
dat_to_csv(dat_name, csv_name)
print("done")