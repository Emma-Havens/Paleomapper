#import shapefile
import os
import numpy as np
import datetime
import sys
import math

latpoint = []
lonpoint = []
pentype = []
record_count = 0

#
# Open geographic data file - will need to update to allow for more than one geographic data file
#
print('\n\n\nThis program converts Paleomap format .dat file to a Plates File format for opening in GPlates')
infile = input("\nEnter Input Paleomap GEOGRAPHIC .DAT file: ")
in_geog_file = open(infile, 'r')
outfile = input("\nEnter Output .DAT file converted to PLATES format: ")
out_geog_file = open(outfile, 'w')

#Intialize variables
valid_choice = True
geographic_records_to_read = True

# this while loop goes until end of file is encountered.  It returns to this location every time
# a lat value of 99.0 is encountered and starts reading next header (two lines)

while geographic_records_to_read == True:
    latpoint = []
    lonpoint = []
    pentype = []
    record_count = 0

    header1 = in_geog_file.readline()  #1st plate_id header line readline will read the entire record

    if (header1 == ""):
        print ("File Finished")
        break
#    
#write out  the first line of the header into the out file    
    out_geog_file.write(header1)

    parser = in_geog_file.readline()  # 2nd line of plate_id header
#        print(parser)
    
    if parser == "":
        break
#
    record_list = parser.split() # parse the record_list into variables
    plateid = int(record_list[0])
    appears = float(record_list[1])
    disappears = float(record_list[2])
    id_type = str(record_list[3])
    id_type_mod = int(record_list[4])
    plateid2 = int(record_list[5])
    color = int(record_list[6])

    valid_records = True
    i = 0
    continue_reading = True
    first_point_after_header =  True
    new_segment = True
    
# process all the records one at a time until encounter a pen of 3, or
# alat = 99 or alat =99.5.  Pen postion 3 indicates that the pen has instantaneously
# moved to the lat/long in same record  and has put back down to continue the point to point,
# so the 3 indicates the start of a new segment

    parser = in_geog_file.readline()  #read first line after header always retain variables
    record_count = record_count + 1

    record_list = parser.split()
    alat = float(record_list[0])
    along = float(record_list[1])
    pen = int(record_list[2])

#store alat, along, pen into a list... this is required in order to first create a count of the number of lat/long points betweeen headers
# that must be recorded as a variable in the second line of the header
#
    latpoint.append(alat)
    lonpoint.append(along)
    pentype.append(pen)
    record_count = record_count + 1
    i=i+1
    first_point_after_header =  False

    while (valid_records == True):
        parser = in_geog_file.readline()  #read second line after header and process as required

        record_list = parser.split()
        alat = float(record_list[0])
        along = float(record_list[1])
        pen = int(record_list[2])


# if valid latitude, add records to the list                    

        if (alat <= 90):
            latpoint.append(alat)
            lonpoint.append(along)
            pentype.append(pen)
            record_count = record_count + 1
            i=i+1
#            print(record_count)
            new_segment=False
#            print('alat, along, i = ', alat, along, i)
       
        if (alat > 90):
#            print('Encountered 99 for alat')
            new_segment = True

            out_geog_file.write('%4d%7.1f%7.1f%3s%4d%4d%4d%6d\n' % (plateid,appears,disappears,id_type,id_type_mod,plateid2,color,record_count-1))
            
#write out the lat, long, pen to the file and start the process again 

            for x in range(0,i):
                out_geog_file.write('%9.4f%10.4f%2d\n' % (float(latpoint[x]), float(lonpoint[x]), int(pentype[x])))
            out_geog_file.write("  99.0000   99.0000 3\n")

            first_point_after_header =  True
            valid_records = False


#reassign variables for startover, but first must capture the point where the pen = 3 was encountered
##
        if ((new_segment == True) and (valid_records == True)):
            first_point_after_header = False
            i = 0


in_geog_file.close()
out_geog_file.close()
