from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QComboBox, QRadioButton, QButtonGroup, QTableView,
    QAbstractItemView, QHeaderView, QCheckBox, QApplication, QStatusBar, QProgressBar
    )
from PySide6.QtGui import QIntValidator, QDoubleValidator, QIcon
from PySide6.QtCore import Qt

import os
import traceback
import sys
import numpy as np

import file_handling
import matplotlib.pyplot as plt
from geo_file_table import CheckBoxDelegate, ArrowDelegate, FileTableModel
from draw_map_gui import Figure
from create_kml import saveKML
from create_dat import saveDAT
from rotation_engine_class import RotationEngine

class UserInterrupt(Exception):
    pass

class PlateTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PaleoMapper")
        self.setGeometry(100, 100, 400, 700)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Window icon and status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        pm_icon_light = QIcon('PM_icon_lightbg.png')
        icon_light = QLabel()
        icon_light.setPixmap(pm_icon_light.pixmap(25, 25))
        self.status_bar.addPermanentWidget(icon_light)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(5)


        # Geographic file input
        file_controls_layout = QHBoxLayout()
        self.load_project_button = QPushButton("Load Project")
        self.load_project_button.clicked.connect(self.load_project)
        self.save_project_button = QPushButton("Save Project")
        self.add_file_button = QPushButton("Add File")
        self.add_file_button.clicked.connect(self.add_geo_file)
        self.remove_file_button = QPushButton("Remove File")
        self.remove_file_button.clicked.connect(self.remove_selected_file)
        file_controls_layout.addWidget(QLabel("Geographic Files:"))
        file_controls_layout.addWidget(self.load_project_button)
        file_controls_layout.addWidget(self.save_project_button)
        file_controls_layout.addWidget(self.add_file_button)
        file_controls_layout.addWidget(self.remove_file_button)

        # Create table view
        self.file_table = QTableView()
        self.file_model = FileTableModel()
        self.file_table.setModel(self.file_model)
        self._arrow_delegate = ArrowDelegate()  # Store as instance attribute
        self._checkbox_delegate = CheckBoxDelegate()
        self.file_table.setItemDelegateForColumn(1, self._arrow_delegate)
        self.file_table.setItemDelegateForColumn(0, self._checkbox_delegate)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.file_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed) 

        # Rotation file input
        rotation_layout = QHBoxLayout()
        rotation_file_label = QLabel("Rotation File:")
        self.rotation_file_entry = QLineEdit()
        if os.path.isfile(self.file_model.rot_file):
            self.rotation_file_entry.setText(self.file_model.rot_file)
        rotation_file_button = QPushButton("Open")
        rotation_file_button.clicked.connect(self.browse_rotation_file)  
        rotation_layout.addWidget(rotation_file_label)
        rotation_layout.addWidget(rotation_file_button)
        rotation_layout.addWidget(self.rotation_file_entry) 

        # Fixed plate option
        fixed_plate_layout = QHBoxLayout()
        fixed_plate_label = QLabel("Hold a Continent Fixed (Optional):")
        self.fixed_plate_entry = QLineEdit()
        self.fixed_plate_entry.setValidator(QIntValidator())
        self.fixed_plate_entry.setPlaceholderText("Enter Plate ID (e.g., 101 for North America)")
        fixed_plate_layout.addWidget(fixed_plate_label)
        fixed_plate_layout.addWidget(self.fixed_plate_entry)
        
        # Reconstruction time input
        time_label = QLabel("Reconstruction Time (Ma):")
        time_layout = QHBoxLayout()
        self.start_time_entry = QLineEdit()
        self.start_time_entry.setValidator(QDoubleValidator()) 
        self.start_time_entry.setText("0")
        to_label = QLabel(" to ")
        self.end_time_entry = QLineEdit()
        self.end_time_entry.setValidator(QDoubleValidator())
        self.end_time_entry.setPlaceholderText("end animation time (optional)")
        at_label = QLabel(" interval ")
        self.step_time_entry = QLineEdit()
        self.step_time_entry.setValidator(QDoubleValidator())
        self.step_time_entry.setText("10")
        time_layout.addWidget(self.start_time_entry)
        time_layout.addWidget(to_label)
        time_layout.addWidget(self.end_time_entry)
        time_layout.addWidget(at_label)
        time_layout.addWidget(self.step_time_entry)

        # Output options
        output_label = QLabel("Output Options:")
        self.outputs = QButtonGroup()
        self.outputs.setExclusive(False)
        self.outputs.addButton(QCheckBox("Plot to Screen"), 0)
        self.outputs.addButton(QCheckBox("Save as PDF"), 1)
        self.outputs.addButton(QCheckBox("Save as Animation (MP4)"), 2)
        self.outputs.addButton(QCheckBox("Save as DAT"), 3)
        self.outputs.addButton(QCheckBox("Save as KML"), 4)
        self.outputs.button(0).setChecked(True)
        outputs_checkbox_layout = QHBoxLayout()
        for button in self.outputs.buttons(): outputs_checkbox_layout.addWidget(button)
        self.output_inputs_layout = QVBoxLayout()
        self.outputs.buttonClicked.connect(self.toggle_output_inputs)
        self.toggle_output_inputs()

        # Run button
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run)

        # Stop button (initially disabled)
        self.stop_button = QPushButton("Stop Animation")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.handle_stop)
        exec_layout = QHBoxLayout()
        exec_layout.addWidget(self.run_button)
        exec_layout.addWidget(self.stop_button)

        # Add widgets to layout
        self.layout.addLayout(rotation_layout)
        self.layout.addLayout(file_controls_layout)
        self.layout.addWidget(self.file_table)
        self.layout.addLayout(fixed_plate_layout)
        self.layout.addWidget(time_label)
        self.layout.addLayout(time_layout)
        self.layout.addWidget(output_label)
        self.layout.addLayout(outputs_checkbox_layout)
        self.layout.addLayout(self.output_inputs_layout)
        self.layout.addLayout(exec_layout)

    def load_project(self):
        proj_file, _ = QFileDialog.getOpenFileName(
            self, "Select Project File", "", "Project Files (*.json)"
        )
        self.file_model.change_project_file(proj_file)
    
    def add_geo_file(self):
        files_to_add, _ = QFileDialog.getOpenFileNames(
            self, "Select Geographic Files", "", "Geo Files (*.dat *.gpml *.csv)"
        )
        for file in files_to_add:
            self.file_model.add_file(file)
    
    def remove_selected_file(self):
        selected = self.file_table.selectionModel().selectedRows()
        for index in sorted(selected, reverse=True):
            self.file_model.remove_row(index.row())

    def get_geo_files(self):
        files = self.file_model.files
        checked_files = list(filter(lambda file: file[0], files)) # file[0] is boolean of checked box
        checked_files.reverse() # respects proper plotting order
        return checked_files
    
    def browse_rotation_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Rotation File", "", "ROT Files (*.rot)")
        if file:
            self.rotation_file_entry.setText(file)

    def handle_stop(self):
        self.should_stop = True
        self.stop_button.setEnabled(False)
        self.run_button.setEnabled(True)
        self.status_bar.removeWidget(self.progress_bar)
        
        # Close any active matplotlib figures
        plt.close('all')
    
    def clear_layout(self, layout):
        """Recursively clear all widgets and layouts from the given layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                # If the item is a widget, delete it
                widget.deleteLater()
            else:
                # If the item is a layout, recursively clear it
                sub_layout = item.layout()
                if sub_layout:
                    self.clear_layout(sub_layout)
    
    def toggle_output_inputs(self):

        # Clear all existing widgets and layouts
        self.clear_layout(self.output_inputs_layout)
         
        output_options = [self.outputs.id(button) for button in self.outputs.buttons() if button.isChecked()]
        
        if 0 in output_options or 1 in output_options or 2 in output_options: # Screen output
            projection_layout = QHBoxLayout()
            projection_label = QLabel("Map Projection:")
            self.projection_combo = QComboBox()
            self.projection_combo.addItems([
                "Rectilinear",
                "Orthographic",
                "Robinson",
                "Mollweide",
                "Mercator",
                "Transverse Mercator",
                "Miller",
                "Azimuthal Equidistant",
                "Stereographic"
            ])
            self.projection_combo.setMaximumWidth(200)
            projection_layout.addWidget(projection_label)
            projection_layout.addWidget(self.projection_combo)
            projection_layout.addStretch()

            # Lat and Lon lines
            lat_label = QLabel("Latitude Spacing:")
            self.lat_spacing = QLineEdit()
            self.lat_spacing.setValidator(QIntValidator())
            self.lat_spacing.setText("30")
            lon_label = QLabel("Longitude Spacing:")
            self.lon_spacing = QLineEdit()
            self.lon_spacing.setValidator(QIntValidator())
            self.lon_spacing.setText("60")
            self.no_graticule_checkbox = QCheckBox("No Graticules")

            latlon_layout = QHBoxLayout()
            latlon_layout.addWidget(lat_label)
            latlon_layout.addWidget(self.lat_spacing)
            latlon_layout.addWidget(lon_label)
            latlon_layout.addWidget(self.lon_spacing)
            latlon_layout.addWidget(self.no_graticule_checkbox)

            # Additional inputs for specific projections
            self.additional_inputs_layout = QVBoxLayout()
            self.projection_combo.currentIndexChanged.connect(self.toggle_projection_inputs)
            self.toggle_projection_inputs()

            self.output_inputs_layout.addLayout(projection_layout)
            self.output_inputs_layout.addLayout(latlon_layout)
            self.output_inputs_layout.addLayout(self.additional_inputs_layout)

            self.save_fig = {"plot": False, "save": False, "anim": False}
            if 0 in output_options:
                self.save_fig["plot"] = True
            if 1 in output_options:
                pdf_file_label = QLabel("Output .pdf file name:")
                self.pdf_file_entry = QLineEdit()
                self.pdf_file_entry.setText("output.pdf")

                pdf_layout = QHBoxLayout()
                pdf_layout.addWidget(pdf_file_label)
                pdf_layout.addWidget(self.pdf_file_entry)
                self.output_inputs_layout.addLayout(pdf_layout)
            if 2 in output_options:
                self.save_fig["anim"] = True
                mp4_file_label = QLabel("Output .mp4 file name:")
                self.mp4_file_entry = QLineEdit()
                self.mp4_file_entry.setText("output.mp4")
                fps_label = QLabel("Frames per second:")
                self.fps_entry = QLineEdit()
                self.fps_entry.setValidator(QIntValidator())
                self.fps_entry.setText("6")

                mp4_layout = QHBoxLayout()
                mp4_layout.addWidget(mp4_file_label)
                mp4_layout.addWidget(self.mp4_file_entry)
                mp4_layout.addWidget(fps_label)
                mp4_layout.addWidget(self.fps_entry)
                self.output_inputs_layout.addLayout(mp4_layout)
        
        if 3 in output_options:    # DAT file
            dat_file_label = QLabel("Output .dat file name:")
            self.dat_file_entry = QLineEdit()
            self.dat_file_entry.setText("output.dat")

            dat_layout = QHBoxLayout()
            dat_layout.addWidget(dat_file_label)
            dat_layout.addWidget(self.dat_file_entry)

            self.output_inputs_layout.addLayout(dat_layout)

        if 4 in output_options:    # KML file
            kml_file_label = QLabel("Output .kml file name:")
            self.kml_file_entry = QLineEdit()
            self.kml_file_entry.setText("output.kml")

            kml_layout = QHBoxLayout()
            kml_layout.addWidget(kml_file_label)
            kml_layout.addWidget(self.kml_file_entry)

            self.output_inputs_layout.addLayout(kml_layout)

    def toggle_projection_inputs(self):
        """Show or hide additional inputs based on the selected projection."""
        # Clear all existing widgets and layouts
        self.clear_layout(self.additional_inputs_layout)

        # Add inputs for specific projections
        projection_option = self.projection_combo.currentIndex()
        if projection_option in [3, 2, 6, 4, 0]: # Mollweide Robinson Miller Mercator Rectilinear

            # map boundaries
            bounds_label = QLabel("Map Bounds:")
            
            northern_label = QLabel("Northern:")
            self.northern_bound = QLineEdit()
            self.northern_bound.setValidator(QIntValidator())
            self.northern_bound.setText("90")
            
            southern_label = QLabel("Southern:")
            self.southern_bound = QLineEdit()
            self.southern_bound.setValidator(QIntValidator())
            self.southern_bound.setText("-90")
            
            eastern_label = QLabel("Eastern:")
            self.eastern_bound = QLineEdit()
            self.eastern_bound.setValidator(QIntValidator())
            self.eastern_bound.setText("180")
            
            western_label = QLabel("Western:")
            self.western_bound = QLineEdit()
            self.western_bound.setValidator(QIntValidator())
            self.western_bound.setText("-180")

            bounds_layout = QHBoxLayout()
            bounds_layout.addWidget(northern_label)
            bounds_layout.addWidget(self.northern_bound)
            bounds_layout.addWidget(southern_label)
            bounds_layout.addWidget(self.southern_bound)
            bounds_layout.addWidget(eastern_label)
            bounds_layout.addWidget(self.eastern_bound)
            bounds_layout.addWidget(western_label)
            bounds_layout.addWidget(self.western_bound) 

            self.additional_inputs_layout.addWidget(bounds_label)
            self.additional_inputs_layout.addLayout(bounds_layout)          

        elif projection_option in [1, 7, 5]:  # Orthographic AziEqui TransMerc

            # center coordinates
            latlon_layout = QHBoxLayout()
            center_lat_label = QLabel("Center Latitude:")
            self.center_lat_entry = QLineEdit()
            self.center_lat_entry.setValidator(QIntValidator())
            self.center_lat_entry.setText("0")
            center_lon_label = QLabel("Center Longitude:")
            self.center_lon_entry = QLineEdit()
            self.center_lon_entry.setValidator(QIntValidator())
            self.center_lon_entry.setText("0")

            latlon_layout.addWidget(center_lat_label)
            latlon_layout.addWidget(self.center_lat_entry)
            latlon_layout.addWidget(center_lon_label)
            latlon_layout.addWidget(self.center_lon_entry)
            self.additional_inputs_layout.addLayout(latlon_layout)

        elif projection_option == 8:  # Stereographic Plot

            # hemisphere selection
            hemisphere_layout = QHBoxLayout()
            hemisphere_label = QLabel("Hemisphere:")
            hemisphere_group = QButtonGroup(self)
            self.northern_hemisphere = QRadioButton("Northern")
            southern_hemisphere = QRadioButton("Southern")
            self.northern_hemisphere.setChecked(True)  # Default to Northern Hemisphere
            hemisphere_group.addButton(self.northern_hemisphere)
            hemisphere_group.addButton(southern_hemisphere)

            # Minimum Latitude selection
            min_lat_label = QLabel("Minimum Latitude:")
            self.min_lat_entry = QLineEdit()
            self.min_lat_entry.setValidator(QIntValidator())
            self.min_lat_entry.setText("60")

            hemisphere_layout.addWidget(hemisphere_label)
            hemisphere_layout.addWidget(self.northern_hemisphere)
            hemisphere_layout.addWidget(southern_hemisphere)
            hemisphere_layout.addWidget(min_lat_label)
            hemisphere_layout.addWidget(self.min_lat_entry)

            self.additional_inputs_layout.addLayout(hemisphere_layout)

    def run(self):
        try:
            self.should_stop = False
            self.stop_button.setEnabled(True)
            self.run_button.setEnabled(False)
            self.status_bar.addWidget(self.progress_bar)
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.progress_bar.repaint()
            QApplication.processEvents()

            rotation_file = self.rotation_file_entry.text()
            geo_files = self.get_geo_files()
            time_array = self.get_time_bounds(self.start_time_entry.text(), 
                                              self.end_time_entry.text(), self.step_time_entry.text())
            fixed_plate = self.fixed_plate_entry.text()
            output_options = [self.outputs.id(button) for button in self.outputs.buttons() if button.isChecked()]
            if not os.path.isdir("output"): os.mkdir("output")
            print("read in files", flush=True)

            # Validate inputs
            if not rotation_file or not geo_files or time_array is None:
                QMessageBox.critical(self, "Error", "Please fill in all required fields.")
                self.handle_stop()
                return
            if time_array is False:
                QMessageBox.warning(self, "Bad Interval", "Please enter a time interval that divides evenly into the range")
                self.handle_stop()
                return
            print("validate fields", flush=True)
            self.progress_bar.setValue(1)
            self.progress_bar.repaint()
            QApplication.processEvents() 

            figure = self.set_up_map(output_options)
            self.progress_bar.setValue(2)
            self.progress_bar.repaint()
            QApplication.processEvents()
            
            # Set output path
            output_folder = "output/"
            if getattr(sys, 'frozen', False):
                exec_dir = os.path.dirname(sys.executable)
                output_folder = exec_dir + "/" + output_folder
                print(output_folder)
            
            # generate each figure
            for time in time_array:
                self.progress_bar.setValue(3)
                self.progress_bar.repaint()
                QApplication.processEvents()
                if self.should_stop:
                    raise UserInterrupt("Execution stopped by user")

                # solve plate rotations
                engine = RotationEngine()
                engine.rotfnd(rotation_file, time)
                if fixed_plate:
                    engine.hold_fixed_option(int(fixed_plate))
                print("solve rotations")

                # Read in plate by plate
                plate_generator = file_handling.read_files(geo_files, time)
                print("read in plates")
            
                # Rotate each plate
                processed_plate_generator = engine.process_chunks(plate_generator)
                print("process plates")

                # Handle output
                if 3 in output_options:    # Save DAT
                    try:
                        dat_name = output_folder + self.dat_file_entry.text()
                        dat_file = saveDAT(dat_name)
                        processed_plate_generator = dat_file.save_to_dat(processed_plate_generator, time)
                        print("save to dat")
                        QMessageBox.about(self, "Success", f"DAT output saved to {os.path.basename(dat_name)}")
                    except Exception as e:
                        QMessageBox.warning(self, "An Error occurred:", str(e))
                        self.print_error_to_terminal(e)
                
                if 4 in output_options:    # Save KML
                    try:
                        kml_name = output_folder + self.kml_file_entry.text()
                        kml_file = saveKML(kml_name)
                        processed_plate_generator = kml_file.save_to_kml(processed_plate_generator)
                        print("save to kml")
                        QMessageBox.about(self, "Success", f"KML output saved to {os.path.basename(kml_name)}")
                    except Exception as e:
                        QMessageBox.warning(self, "An Error occurred:", str(e))
                        self.print_error_to_terminal(e)

                if 0 in output_options or 1 in output_options or 2 in output_options:  # Plot to Screen
                    # different file name
                    if 1 in output_options:
                        pdf_file = output_folder + self.pdf_file_entry.text()
                        if pdf_file[-4:] == ".pdf": pdf_file = pdf_file[:-4]    # remove file extension, if any
                        if len(time_array) > 1:
                            self.save_fig["save"] = pdf_file + "_" + str(time)
                        else:
                            self.save_fig["save"] = pdf_file

                    try:
                        figure.update_plot_vars(self.save_fig, time)
                        processed_plate_generator = figure.plot_to_screen(processed_plate_generator)
                        print("plot to screen")
                        if 1 in output_options and len(time_array) == 1:
                            QMessageBox.about(self, "Success", f"PDF output saved to {os.path.basename(pdf_file)}")
                    except Exception as e:
                        QMessageBox.warning(self, "An Error occurred:", str(e))
                        self.print_error_to_terminal(e)

                # ensures previous generator functions run through
                for chunk in processed_plate_generator:
                    pass

                QApplication.processEvents()
                self.progress_bar.setValue(4)
                self.progress_bar.repaint()
                QApplication.processEvents()

            # if making animation, assemble now
            if 2 in output_options:
                try:
                    mp4_file = output_folder + self.mp4_file_entry.text()
                    if mp4_file[-4:] != ".mp4": mp4_file = mp4_file + ".mp4"    # add mp4 extension
                    fps = self.fps_entry.text() if self.fps_entry.text() else 6
                    figure.make_animation(mp4_file, fps)
                    QMessageBox.about(self, "Success", f"MP4 output saved to {os.path.basename(mp4_file)}")
                except Exception as e:
                    QMessageBox.warning(self, "An Error occurred:", str(e))
                    self.print_error_to_terminal(e)

            self.progress_bar.setValue(5)
            self.progress_bar.repaint()
            QApplication.processEvents()
            self.stop_button.setEnabled(False)
            self.run_button.setEnabled(True)
            self.status_bar.removeWidget(self.progress_bar)

        except UserInterrupt:
            QMessageBox.about(self, "Animation Halted", "Animation successfully halted")
            print("User halted program")
        except EOFError as rot_error:
            QMessageBox.warning(self, "An Error occurred:", str(rot_error))
            self.print_error_to_terminal(rot_error)
        except ValueError as err:
            QMessageBox.warning(self, "An Error occurred:", str(err))
            self.print_error_to_terminal(err)
        except Exception as err:
            QMessageBox.warning(self, "An Error occurred:", 
                                "A bug has been found or there is an error in an input file. " \
                                "Please change parameters and try again.")
            self.print_error_to_terminal(err)

    def get_time_bounds(self, start_text, end_text, step_text):
        if not start_text: return None
        if not end_text: return [float(start_text)]
        start = float(start_text)
        end = float(end_text)
        if not step_text: 
            step = (end - start) / 10.0
        else:
            step = float(step_text)
        if step == 0:
            QMessageBox.warning(self, "Invalid Step", "Interval cannot be 0")
            return False
        if (end - start) % step != 0.0: return False
        
        print(f"start: {start} end: {end} step: {step}")
        if start < end:
            time_array = np.linspace(start, end, int((end - start) / step) + 1)
        else:
            reversed_time_array = np.linspace(end, start, int((start - end) / step) + 1)
            time_array = np.flip(reversed_time_array)

        return time_array
    
    def set_up_map(self, output_options):
        # Set up map, if needed
        if 0 in output_options or 1 in output_options or 2 in output_options:  # Plot to Screen
            # Collect additional inputs for the projection
            proj_kwargs = {}
            if self.no_graticule_checkbox.isChecked():
                proj_kwargs["lat_spacing"] = 180
                proj_kwargs["lon_spacing"] = 720
            else:
                proj_kwargs["lat_spacing"] = int(self.lat_spacing.text())
                proj_kwargs["lon_spacing"] = int(self.lon_spacing.text())
            print("collect lat/lon spacing")
            
            projection_option = self.projection_combo.currentIndex()
            print(projection_option)
            if projection_option in [3, 2, 6, 4, 0]:  # Mollweide Robinson Mercator Rectilinear 
                # map boundaries
                north_bound = int(self.northern_bound.text())
                south_bound = int(self.southern_bound.text())
                east_bound = int(self.eastern_bound.text())
                west_bound = int(self.western_bound.text())
                print("collect map bounds")

                if (north_bound < south_bound or east_bound < west_bound):
                    QMessageBox.critical(self, "Error", "Unresolvable bounds provided.")
                    return
                print("resolve bounds")
                
                proj_kwargs["map_bounds"] = [west_bound, east_bound, south_bound, north_bound]
            
            elif projection_option in [1, 7, 5]:  # Orthographic AziEqui TransMerc
                # central coordinates
                proj_kwargs["center_lat"] = float(self.center_lat_entry.text())
                proj_kwargs["center_lon"] = float(self.center_lon_entry.text())
                print("collect center point")
            
            elif projection_option == 8:  # Stereographic Plot
                # hemisphere selection
                proj_kwargs["north_hemi"] = self.northern_hemisphere.isChecked()
                proj_kwargs["min_lat"] = int(self.min_lat_entry.text())
                print("collect hemisphere")

            figure = Figure(projection_option, **proj_kwargs)
            print("initialize figure")
            return figure
        
        return None

    def print_error_to_terminal(self, e):
        print("An Error occured:")
        print(type(e))
        traceback.print_tb(e.__traceback__)
        print(e)
        self.handle_stop()