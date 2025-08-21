import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

if __name__ == "__main__":
    
    # Check for existing QApplication
    app = QApplication(sys.argv)
    pm_icon = QIcon('PM_icon_darkbg.png')
    app.setWindowIcon(pm_icon)

    # DO NOT MOVE IMPORT: pygplates (loaded implicitly) will cause segfault
    from gui import PlateTrackerApp
    window = PlateTrackerApp()
    window.show()
    
    sys.exit(app.exec())

# FUTURE TODO
# Raster background
# import shp file?
# can the animaton features be greyed out unless end value entered?

# NOW TODO
# font without polygon?
# color index
# fix polyfill

# DONE
# Read in dat colors
# Fix .dat for .gpml, .dat, .csv
# Fix orthographic projection—empty box
# Change plotting to matplotlib paths
# Integrate fill color into plot_to_screen(), but it looks very bad when crossing the dateline
# polygons missing last point (pygplates error in get_points()/to_lat_long_list())
# not properly handling mutliple geometries on the same features—separate into multiple chunks?
# up and down arrows to move file rows
# dat saves h1 comma delimited with proper multicolor read
# output .png and make to screen always active
# add other map projections
# add animation
# fps default 6
# animation changes: mybp -> Ma, add checker to see if animate forwards or backwards, 'at' -> 'interval'
# change step to always be (on default) 10 images for the interval
# input output folders
# kill button
# Success saving dat or kml message box
# remove plot time int validator
# return Run button to active after Error message

# KNOWN PROBLEMS
# fix csv into kml
# Seg fault: 11
# northern/southern extent don't always work right?
# animate no step diff between start and end <10
# persistent seg fault on Chris's machine
# plotted animation won't progress if saving pdfs

# polygon fill problems:
# problem 165: polygon splitting algorithm sorting breaks down at poles and can fill in intervening space
# problem 406 mollweide v ortho: curvature in orthographic projection inverts skinny polyogn and fills globe, 0 and 60
# Robinson ocean fill same cause??
# transverse fucked up ocean
# aziequi 90,0--something is filling the ocean
# none,multi north stereo--all one color and problem filling at pole
# transverse mercator 320--its bad
# pole_text_test.csv error


# pyinstaller --clean main.spec