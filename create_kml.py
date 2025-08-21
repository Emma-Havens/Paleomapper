import simplekml
import matplotlib.colors

class saveKML:

    def __init__(self, kml_file):
        file_extension = kml_file[-4:]
        if file_extension == ".kml":
            self.kml_file = kml_file
        else:
            self.kml_file = kml_file + ".kml"
        
    def save_to_kml(self, chunk_generator):

        kml = simplekml.Kml(name = self.kml_file, open=1)
        
        for chunk in chunk_generator:
            # Extract header information
            plateid = chunk.plateid
            appears = chunk.appears
            disappears = chunk.disappears
            id_type = chunk.feature_type
            plateid2 = chunk.plateid2
            label = chunk.label
            bcolor = chunk.border_color

            hex_color = matplotlib.colors.to_hex(bcolor)

            # True if the most recently processed point was a pen up command
            prev_penup = False
            
            # Process records
            points = []
            for record in chunk.records:
                alat = record.alat
                along = record.along
                pen = record.pen
                
                if alat < 99.0:
                    if pen == 2:  # Pen down
                        points.append((along, alat))
                        prev_penup = False

                    elif pen == 3:  # Pen up
                        
                        # Don't store 2 penups in a row, only need the latest one
                        if prev_penup:
                            points.pop()

                        if points:

                            # If all stored points are the same, just save one point
                            if points.count(points[0]) == len(points):
                                value = kml.newpoint(name="A Point", coords=[points[0]])
                                value.style.iconstyle.color = hex_color

                            # Otherwise, plot the whole line
                            else:
                                value = kml.newlinestring(name="A Line")
                                value.coords = points
                                value.style.linestyle.color = hex_color
                                
                            # Either way, add extended data attributes
                            value.extendeddata.newdata(name='Plate_ID1', value=plateid, displayname="Plate ID1")
                            value.extendeddata.newdata(name='Appears', value=appears, displayname="Appear Age")
                            value.extendeddata.newdata(name='Disappears', value=disappears, displayname="Disappear Age")
                            value.extendeddata.newdata(name='ID_Type', value=id_type, displayname="ID Type")
                            value.extendeddata.newdata(name='Label', value=label, displayname="Label")
                            value.extendeddata.newdata(name='PlateID2', value=plateid2, displayname="Plate ID2")
                        
                        points = []
                        points.append((along, alat))
                        prev_penup = True
            
            # Add any remaining points
            if points:

                # Don't plot the last point if it was a penup
                if prev_penup:
                    points.pop()

                if points:
                    # If all stored points are the same, just save one point
                    if points.count(points[0]) == len(points):
                        value = kml.newpoint(name="A Point", coords=[points[0]])
                        value.style.iconstyle.color = hex_color

                    # Otherwise, plot the whole line
                    else:
                        value = kml.newlinestring(name="A Line")
                        value.coords = points
                        value.style.linestyle.color = hex_color
                        
                    # Either way, add extended data attributes
                    value.extendeddata.newdata(name='Plate_ID1', value=plateid, displayname="Plate ID1")
                    value.extendeddata.newdata(name='Appears', value=appears, displayname="Appear Age")
                    value.extendeddata.newdata(name='Disappears', value=disappears, displayname="Disappear Age")
                    value.extendeddata.newdata(name='ID_Type', value=id_type, displayname="ID Type")
                    value.extendeddata.newdata(name='Label', value=label, displayname="Label")
                    value.extendeddata.newdata(name='PlateID2', value=plateid2, displayname="Plate ID2")

            yield chunk
        
        kml.save(self.kml_file)


        # 2 pen=3 in a row
        # duplicate coordinates