from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QComboBox, QRadioButton, QButtonGroup, QTableView,
    QAbstractItemView, QHeaderView, QCheckBox, QApplication, QStatusBar, QProgressBar, QSplitter, QFrame,
    QFormLayout
    )
from PySide6.QtGui import QIntValidator, QDoubleValidator, QIcon, QAction
from PySide6.QtCore import Qt

import os
import traceback
import sys
import numpy as np

import global_vars
import main_menu
import file_handling
import matplotlib.pyplot as plt
from geo_file_table import CheckBoxDelegate, ArrowDelegate, FileTableModel, RasterTableModel
from draw_map_gui import Figure
from create_kml import saveKML
from create_dat import saveDAT
from create_output import saveFile
from rotation_engine_class import RotationEngine

class UserInterrupt(Exception):
    pass

class PlateTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PaleoMapper")
        QApplication.setApplicationDisplayName("PaleoMapper")
        QApplication.setApplicationName("PaleoMapper")
        self.setGeometry(100, 0, 650, 900)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Menu Bar
        top_menu = self.menuBar()
        general_menu = top_menu.addMenu("General")
        self.preferences = main_menu.PreferenceDialog()
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.preferences.show_window)
        general_menu.addAction(preferences_action)
        if global_vars.configs.get("use_recent_proj"):
            project_to_open = global_vars.configs.get("most_recent_path")
        else:
            project_to_open = global_vars.configs.get("default_proj")
        
        self.about_dialog = main_menu.AboutDialog()
        about_action = QAction("About Paleomapper", self)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about_dialog.show_window)
        general_menu.addAction(about_action)
        
        self.faq_dialog = main_menu.FAQDialog()
        faq_action = QAction("FAQ", self)
        faq_action.triggered.connect(self.faq_dialog.show_window)
        general_menu.addAction(faq_action)
        general_menu.addSeparator()
        
        self.color_dialog = main_menu.ColorDialog()
        color_options_action = QAction("Color Options", self)
        color_options_action.triggered.connect(self.color_dialog.show_window)
        general_menu.addAction(color_options_action)

        # Window icon and status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # pm_icon_light = QIcon('PM_icon_lightbg.png')
        pm_icon_light = QIcon(global_vars.logo_path)
        icon_light = QLabel()
        icon_light.setPixmap(pm_icon_light.pixmap(25, 25))
        self.status_bar.addPermanentWidget(icon_light)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(5)

        # Geographic file input
        file_controls_layout = QHBoxLayout()
        self.add_file_button = QPushButton("Add File")
        self.add_file_button.clicked.connect(self.add_file)
        self.remove_file_button = QPushButton("Remove File")
        self.remove_file_button.clicked.connect(self.remove_selected_file)
        self.clear_table_button = QPushButton("Clear Table")
        self.clear_table_button.clicked.connect(self.clear_table)
        file_controls_layout.addWidget(QLabel("Geographic Files:"))
        file_controls_layout.addStretch()
        file_controls_layout.addWidget(self.add_file_button)
        file_controls_layout.addWidget(self.remove_file_button)
        file_controls_layout.addWidget(self.clear_table_button)

        # Create raster table
        self.raster_table = QTableView()
        self.raster_model = RasterTableModel()
        self.raster_table.setModel(self.raster_model)
        self._arrow_delegate_raster = ArrowDelegate()  # Store as instance attribute
        self._checkbox_delegate_raster = CheckBoxDelegate()
        self.raster_table.setItemDelegateForColumn(1, self._arrow_delegate_raster)
        self.raster_table.setItemDelegateForColumn(0, self._checkbox_delegate_raster)
        self.raster_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.raster_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.raster_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.raster_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.raster_table.horizontalHeader().resizeSection(3, 130)
        self.raster_table.horizontalHeader().resizeSection(4, 70)
        self.raster_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed) 

        # Create file table
        self.file_table = QTableView()
        self.file_model = FileTableModel(self.raster_model, project_to_open)
        self.file_table.setModel(self.file_model)
        self._arrow_delegate = ArrowDelegate()  # Store as instance attribute
        self._checkbox_delegate = CheckBoxDelegate()
        self.file_table.setItemDelegateForColumn(1, self._arrow_delegate)
        self.file_table.setItemDelegateForColumn(0, self._checkbox_delegate)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.file_table.horizontalHeader().resizeSection(5, 70)
        self.file_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed) 

        # Create splitter
        self.table_splitter = QSplitter(Qt.Vertical)
        self.table_splitter.addWidget(self.file_table)
        self.table_splitter.addWidget(self.raster_table)
        self.table_splitter.setSizes([400, 200]) 
        self.table_splitter.setChildrenCollapsible(True) 
        self.table_splitter.setHandleWidth(5) 

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

        # Project Selection widgets
        project_controls_frame = QFrame(self)
        project_controls_frame.setFrameShadow(QFrame.Shadow.Raised)
        project_controls_frame.setFrameShape(QFrame.Shape.Panel)
        project_controls_frame.setStyleSheet("""QFrame {background-color: #F5F5F5;}""")
        project_controls_layout = QHBoxLayout()
        self.project_label = QLabel(os.path.basename(self.file_model.proj_file))
        bolded_font = self.project_label.font()
        bolded_font.setBold(True)
        self.project_label.setFont(bolded_font)
        self.load_project_button = QPushButton("Load Project")
        self.load_project_button.clicked.connect(self.load_project)
        self.save_project_button = QPushButton("Save (Current)")
        self.save_project_button.clicked.connect(self.save_project)
        self.new_project_button = QPushButton("Save (New)")
        self.new_project_button.clicked.connect(self.new_project)
        project_controls_layout.addWidget(QLabel("Current project:"))
        project_controls_layout.addWidget(self.project_label)
        project_controls_layout.addStretch()
        project_controls_layout.addWidget(self.load_project_button)
        project_controls_layout.addWidget(self.save_project_button)
        project_controls_layout.addWidget(self.new_project_button)
        project_controls_frame.setLayout(project_controls_layout)

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
        self.outputs_button_group = QButtonGroup()
        self.outputs_button_group.setExclusive(False)
        self.outputs_button_group.addButton(QCheckBox("Plot to Screen"), 0)
        self.outputs_button_group.addButton(QCheckBox("Save as PDF"), 1)
        self.outputs_button_group.addButton(QCheckBox("Save as Animation (MP4)"), 2)
        self.outputs_button_group.addButton(QCheckBox("Save as SVG"), 7)
        self.outputs_button_group.addButton(QCheckBox("Save as GPML"), 5)
        self.outputs_button_group.addButton(QCheckBox("Save as SHP"), 6)
        self.outputs_button_group.addButton(QCheckBox("Save as DAT"), 3)
        self.outputs_button_group.addButton(QCheckBox("Save as KML"), 4)
        self.outputs_button_group.button(0).setChecked(True)
        outputs_checkbox_layout = QGridLayout()
        num_in_row = 4
        column_count = 4
        for i, button in enumerate(self.outputs_button_group.buttons()):
            outputs_checkbox_layout.addWidget(button, int(i / num_in_row), i % column_count)
        self.output_inputs_layout = QFormLayout()
        self.output_inputs_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.output_inputs_layout.setLabelAlignment(Qt.AlignLeft)
        self.outputs_button_group.idToggled.connect(self.hide_output_inputs)
        self.create_output_inputs()
        self.hide_output_inputs(0)
        self.hide_projection_inputs(0)

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
        self.layout.addWidget(project_controls_frame)
        self.layout.addLayout(rotation_layout)
        self.layout.addLayout(file_controls_layout)
        self.layout.addWidget(self.table_splitter)
        self.layout.addWidget(time_label)
        self.layout.addLayout(time_layout)
        self.layout.addLayout(fixed_plate_layout)
        self.layout.addWidget(output_label)
        self.layout.addLayout(outputs_checkbox_layout)
        self.layout.addLayout(self.output_inputs_layout)
        self.layout.addLayout(exec_layout)

        self.start_time_entry.setFocus()

    def load_project(self):
        proj_file, _ = QFileDialog.getOpenFileName(
            self, "Select Project File", "", "Project Files (*.json)"
        )
        self.file_model.load_project(proj_file)
        self.rotation_file_entry.setText(self.file_model.rot_file)
        self.project_label.setText(os.path.basename(self.file_model.proj_file))
        global_vars.configs.set("most_recent_path", self.file_model.proj_file)
        global_vars.configs.save()
        self.update_raster_table_visibility()
        self.status_bar.showMessage(f"Loaded project {os.path.basename(self.file_model.proj_file)}", 3000)

    def new_project(self):
        proj_file, _ = QFileDialog.getSaveFileName(
            self, "Enter Project File Name", "", "Project Files (*.json)"
        )
        self.file_model.save_project(proj_file)
        self.rotation_file_entry.setText(self.file_model.rot_file)
        self.project_label.setText(os.path.basename(self.file_model.proj_file))
        global_vars.configs.set("most_recent_path", self.file_model.proj_file)
        global_vars.configs.save()
        self.status_bar.showMessage(f"Saved project {os.path.basename(self.file_model.proj_file)}", 3000)

    def save_project(self):
        self.file_model.save_project("", True)
        self.rotation_file_entry.setText(self.file_model.rot_file)
        self.status_bar.showMessage(f"Saved project {os.path.basename(self.file_model.proj_file)}", 3000)
    
    def add_file(self):
        files_to_add, _ = QFileDialog.getOpenFileNames(
            self, "Select Geographic Files", "", "Geo Files (*.dat *.gpml *.csv *.shp *.jpg *.jpeg *.png)"
        )
        for file in files_to_add:
            if os.path.splitext(file)[1] in self.file_model.accepted_extensions:
                self.file_model.add_file(file)
            else:
                self.raster_model.add_file(file)
        self.update_raster_table_visibility()
    
    def remove_selected_file(self):
        selected = self.file_table.selectionModel().selectedRows()
        for index in sorted(selected, reverse=True):
            self.file_model.remove_row(index.row())
        selected = self.raster_table.selectionModel().selectedRows()
        for index in sorted(selected, reverse=True):
            self.raster_model.remove_row(index.row())
        self.update_raster_table_visibility()

    def clear_table(self):
        for _ in range(self.file_model.rowCount()):
            self.file_model.remove_row(0)
        for _ in range(self.raster_model.rowCount()):
            self.raster_model.remove_row(0)
        self.update_raster_table_visibility()

    def get_geo_files(self):
        files = self.file_model.files
        print(files)
        checked_files = list(filter(lambda file: file[0], files)) # file[0] is boolean of checked box
        checked_files.reverse() # respects proper plotting order
        return checked_files
    
    def get_raster_files(self):
        files = self.raster_model.files
        print(files)
        checked_files = list(filter(lambda file: file[0], files)) # file[0] is boolean of checked box
        checked_files.reverse() # respects proper plotting order
        return checked_files
    
    def browse_rotation_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Rotation File", "", "ROT Files (*.rot)")
        if file:
            self.rotation_file_entry.setText(file)
            self.file_model.rot_file = file

    def handle_stop(self):
        self.should_stop = True
        self.stop_button.setEnabled(False)
        self.run_button.setEnabled(True)
        self.status_bar.removeWidget(self.progress_bar)
        
        # Close any active matplotlib figures
        plt.close('all')
    
    def update_raster_table_visibility(self):
        if self.raster_model.rowCount() > 0:
            if self.table_splitter.sizes()[1] == 0:
                self.table_splitter.setSizes([400, 200]) 
        else:
            if self.table_splitter.sizes()[1] > 0:
                self.table_splitter.setSizes([600, 0])
            
        self.table_splitter.updateGeometry()
        QApplication.processEvents()
    
    def set_default_output_file_name(self, time):
        edit_list = [ [self.pdf_file_entry, ".pdf"], [self.mp4_file_entry, ".mp4"],
                      [self.svg_file_entry, ".svg"], [self.gpml_file_entry, ".gpml"],
                      [self.shp_file_entry, ".shp"], [self.dat_file_entry, ".dat"],
                      [self.kml_file_entry, ".kml"] ]
        proj_name = self.file_model.get_proj_name() if self.file_model.get_proj_name() else "output"
        for (output_edit, extension) in edit_list:
            # if text hasn't been set, elif still starts with "<time>Ma_"
            if output_edit.text() == "":
                default_output_name = time + "Ma_" + proj_name + extension
                output_edit.setText(default_output_name)
            elif output_edit.text().split("_")[0][-2:] == "Ma":
                # gets everything after "<time>Ma_"
                user_modified_name = "_".join(output_edit.text().split("_")[1:])
                modified_output_name = time + "Ma_" + user_modified_name
                output_edit.setText(modified_output_name)
    
    def hide_output_inputs(self, output_id):
        on_or_off = self.outputs_button_group.button(output_id).isChecked()
        self.toggled_output_options.append(output_id) if on_or_off else self.toggled_output_options.remove(output_id)
        if (0 in self.toggled_output_options or 1 in self.toggled_output_options or 
                2 in self.toggled_output_options or 7 in self.toggled_output_options):
            need_map_settings = True
        else: need_map_settings = False

        self.output_inputs_layout.setRowVisible(self.projection_layout, need_map_settings)
        self.output_inputs_layout.setRowVisible(self.map_title_layout, need_map_settings)
        self.output_inputs_layout.setRowVisible(self.latlon_layout, need_map_settings)
        self.output_inputs_layout.setRowVisible(self.additional_inputs_layout, need_map_settings)
        
        match output_id:
            case 0: # plot to screen
                self.save_fig["plot"] = on_or_off
            case 1: # pdf
                self.output_inputs_layout.setRowVisible(self.pdf_file_entry, on_or_off)
            case 2: # mp4
                self.save_fig["anim"] = on_or_off
                self.output_inputs_layout.setRowVisible(self.mp4_layout, on_or_off)
            case 3: # dat
                self.output_inputs_layout.setRowVisible(self.dat_file_entry, on_or_off)
            case 4: # kml
                self.output_inputs_layout.setRowVisible(self.kml_file_entry, on_or_off)
            case 5: # gpml
                self.output_inputs_layout.setRowVisible(self.gpml_file_entry, on_or_off)
            case 6: # shp
                self.output_inputs_layout.setRowVisible(self.shp_file_entry, on_or_off)
            case 7: # svg
                self.output_inputs_layout.setRowVisible(self.svg_file_entry, on_or_off)

        projection_index = self.projection_combo.currentIndex() if need_map_settings else -1
        self.hide_projection_inputs(projection_index)
    
    def create_output_inputs(self):
        # Map projection combo box
        self.projection_layout = QHBoxLayout()
        projection_combo_label = QLabel("Map Projection:")
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
        self.projection_layout.addWidget(projection_combo_label)
        self.projection_layout.addWidget(self.projection_combo)
        self.projection_layout.addStretch()
        self.output_inputs_layout.addRow(self.projection_layout)

        # Map title
        self.map_title_layout = QHBoxLayout()
        map_title_label = QLabel("Map Title:")
        self.map_title_edit = QLineEdit()
        self.map_title_edit.setText("{time}Ma")
        self.line_thickness_checkbox = QCheckBox("Plot Thin Lines")
        self.map_title_layout.addWidget(map_title_label)
        self.map_title_layout.addWidget(self.map_title_edit)
        self.map_title_layout.addWidget(self.line_thickness_checkbox)
        self.output_inputs_layout.addRow(self.map_title_layout)

        # Lat and Lon lines
        self.latlon_layout = QHBoxLayout()
        lat_label = QLabel("Latitude Spacing:")
        self.lat_spacing = QLineEdit()
        self.lat_spacing.setValidator(QIntValidator())
        self.lat_spacing.setText("30")
        lon_label = QLabel("Longitude Spacing:")
        self.lon_spacing = QLineEdit()
        self.lon_spacing.setValidator(QIntValidator())
        self.lon_spacing.setText("60")
        self.no_graticule_checkbox = QCheckBox("No Graticule")
        self.latlon_layout.addWidget(lat_label)
        self.latlon_layout.addWidget(self.lat_spacing)
        self.latlon_layout.addWidget(lon_label)
        self.latlon_layout.addWidget(self.lon_spacing)
        self.latlon_layout.addWidget(self.no_graticule_checkbox)
        self.output_inputs_layout.addRow(self.latlon_layout)

        # Additional inputs for specific projections
        self.additional_inputs_layout = QFormLayout()
        self.additional_inputs_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.additional_inputs_layout.setLabelAlignment(Qt.AlignLeft)
        self.projection_combo.currentIndexChanged.connect(self.hide_projection_inputs)
        self.create_projection_inputs()
        self.output_inputs_layout.addRow(self.additional_inputs_layout)

        # pdf
        self.save_fig = {"plot": False, "pdf": False, "anim": False, "svg": False}
        self.pdf_file_entry = QLineEdit()
        self.output_inputs_layout.addRow("Output .pdf file name:", self.pdf_file_entry)

        # mp4
        self.mp4_layout = QHBoxLayout()
        self.mp4_file_entry = QLineEdit()
        fps_label = QLabel("Frames per second:")
        self.fps_entry = QLineEdit()
        self.fps_entry.setValidator(QIntValidator())
        self.fps_entry.setText("6")
        self.mp4_layout.addWidget(self.mp4_file_entry)
        self.mp4_layout.addWidget(fps_label)
        self.mp4_layout.addWidget(self.fps_entry)
        self.output_inputs_layout.addRow("Output .mp4 file name:", self.mp4_layout)

        # svg
        self.svg_file_entry = QLineEdit()
        self.output_inputs_layout.addRow("Output .svg file name:", self.svg_file_entry)
        
        # dat
        self.dat_file_entry = QLineEdit()
        self.output_inputs_layout.addRow("Output .dat file name:", self.dat_file_entry)

        # kml
        self.kml_file_entry = QLineEdit()
        self.output_inputs_layout.addRow("Output .kml file name:", self.kml_file_entry)

        # gpml
        self.gpml_file_entry = QLineEdit()
        self.output_inputs_layout.addRow("Output .gpml file name:", self.gpml_file_entry)

        # shp
        self.shp_file_entry = QLineEdit()
        self.output_inputs_layout.addRow("Output .shp file name:", self.shp_file_entry)

        # set text in line edits
        self.set_default_output_file_name("0")
        self.start_time_entry.textChanged.connect(self.set_default_output_file_name)

        # hide all rows
        self.output_inputs_layout.setRowVisible(self.projection_layout, False)
        self.output_inputs_layout.setRowVisible(self.latlon_layout, False)
        self.output_inputs_layout.setRowVisible(self.additional_inputs_layout, False)
        self.output_inputs_layout.setRowVisible(self.pdf_file_entry, False)
        self.output_inputs_layout.setRowVisible(self.mp4_layout, False)
        self.output_inputs_layout.setRowVisible(self.svg_file_entry, False)
        self.output_inputs_layout.setRowVisible(self.gpml_file_entry, False)
        self.output_inputs_layout.setRowVisible(self.shp_file_entry, False)
        self.output_inputs_layout.setRowVisible(self.dat_file_entry, False)
        self.output_inputs_layout.setRowVisible(self.kml_file_entry, False)
        self.toggled_output_options = []

    def hide_projection_inputs(self, projection_option):
        if projection_option in [3, 2, 6, 4, 0]: # Mollweide Robinson Miller Mercator Rectilinear
            self.additional_inputs_layout.setRowVisible(self.bounds_layout, True)
            self.additional_inputs_layout.setRowVisible(self.center_coord_layout, False)
            self.additional_inputs_layout.setRowVisible(self.hemisphere_layout, False)
        elif projection_option in [1, 5]:  # Orthographic TransMerc
            self.additional_inputs_layout.setRowVisible(self.bounds_layout, False)
            self.additional_inputs_layout.setRowVisible(self.center_coord_layout, True)
            self.additional_inputs_layout.setRowVisible(self.hemisphere_layout, False)
        elif projection_option in [7, 8]:  # AziEqui Stereo
            self.additional_inputs_layout.setRowVisible(self.bounds_layout, False)
            self.additional_inputs_layout.setRowVisible(self.center_coord_layout, False)
            self.additional_inputs_layout.setRowVisible(self.hemisphere_layout, True)
        elif projection_option == -1:  # display no map settings
            self.additional_inputs_layout.setRowVisible(self.bounds_layout, False)
            self.additional_inputs_layout.setRowVisible(self.center_coord_layout, False)
            self.additional_inputs_layout.setRowVisible(self.hemisphere_layout, False)
    
    def create_projection_inputs(self):
        # map boundaries
        self.bounds_layout = QVBoxLayout()
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

        sub_bounds_layout = QHBoxLayout()
        sub_bounds_layout.addWidget(northern_label)
        sub_bounds_layout.addWidget(self.northern_bound)
        sub_bounds_layout.addWidget(southern_label)
        sub_bounds_layout.addWidget(self.southern_bound)
        sub_bounds_layout.addWidget(eastern_label)
        sub_bounds_layout.addWidget(self.eastern_bound)
        sub_bounds_layout.addWidget(western_label)
        sub_bounds_layout.addWidget(self.western_bound) 

        self.bounds_layout.addWidget(bounds_label)
        self.bounds_layout.addLayout(sub_bounds_layout)
        self.additional_inputs_layout.addRow(self.bounds_layout)

        # center coordinates
        self.center_coord_layout = QHBoxLayout()
        center_lat_label = QLabel("Center Latitude:")
        self.center_lat_entry = QLineEdit()
        self.center_lat_entry.setValidator(QIntValidator())
        self.center_lat_entry.setText("0")
        center_lon_label = QLabel("Center Longitude:")
        self.center_lon_entry = QLineEdit()
        self.center_lon_entry.setValidator(QIntValidator())
        self.center_lon_entry.setText("0")
        self.center_coord_layout.addWidget(center_lat_label)
        self.center_coord_layout.addWidget(self.center_lat_entry)
        self.center_coord_layout.addWidget(center_lon_label)
        self.center_coord_layout.addWidget(self.center_lon_entry)
        self.additional_inputs_layout.addRow(self.center_coord_layout)

        # hemisphere selection
        self.hemisphere_layout = QHBoxLayout()
        hemisphere_label = QLabel("Hemisphere:")
        hemisphere_group = QButtonGroup(self)
        self.northern_hemisphere = QRadioButton("Northern")
        southern_hemisphere = QRadioButton("Southern")
        self.northern_hemisphere.setChecked(True)
        hemisphere_group.addButton(self.northern_hemisphere)
        hemisphere_group.addButton(southern_hemisphere)
        min_lat_label = QLabel("Minimum Latitude:")
        self.min_lat_entry = QLineEdit()
        self.min_lat_entry.setValidator(QIntValidator())
        self.min_lat_entry.setText("60")
        self.hemisphere_layout.addWidget(hemisphere_label)
        self.hemisphere_layout.addWidget(self.northern_hemisphere)
        self.hemisphere_layout.addWidget(southern_hemisphere)
        self.hemisphere_layout.addWidget(min_lat_label)
        self.hemisphere_layout.addWidget(self.min_lat_entry)
        self.additional_inputs_layout.addRow(self.hemisphere_layout)

    def run(self):
        try:
            self.should_stop = False
            self.stop_button.setEnabled(True)
            self.run_button.setEnabled(False)
            self.status_bar.clearMessage()
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
            output_options = [self.outputs_button_group.id(button) for button in self.outputs_button_group.buttons() if button.isChecked()]
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
            output_folder = os.path.dirname(self.file_model.proj_file)
            if getattr(sys, 'frozen', False):
                exec_dir = os.path.dirname(sys.executable)
                output_folder = os.path.join(exec_dir, output_folder)
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
                        dat_name = os.path.join(output_folder, self.dat_file_entry.text())
                        dat_file = saveDAT(dat_name)
                        processed_plate_generator = dat_file.save_to_dat(processed_plate_generator, time)
                        print("save to dat")
                        QMessageBox.about(self, "Success", f"DAT output saved to {os.path.basename(dat_name)}")
                    except Exception as e:
                        QMessageBox.warning(self, "An Error occurred:", str(e))
                        self.print_error_to_terminal(e)
                
                if 4 in output_options:    # Save KML
                    try:
                        kml_name = os.path.join(output_folder, self.kml_file_entry.text())
                        kml_file = saveKML(kml_name)
                        processed_plate_generator = kml_file.save_to_kml(processed_plate_generator)
                        print("save to kml")
                        QMessageBox.about(self, "Success", f"KML output saved to {os.path.basename(kml_name)}")
                    except Exception as e:
                        QMessageBox.warning(self, "An Error occurred:", str(e))
                        self.print_error_to_terminal(e)

                if 5 in output_options:    # Save GPML
                    try:
                        gpml_name = os.path.join(output_folder, self.gpml_file_entry.text())
                        gpml_file = saveFile(gpml_name, ".gpml")
                        processed_plate_generator = gpml_file.save_to_file(processed_plate_generator, time)
                        print("save to gpml")
                        QMessageBox.about(self, "Success", f"GPML output saved to {os.path.basename(gpml_name)}")
                    except Exception as e:
                        QMessageBox.warning(self, "An Error occurred:", str(e))
                        self.print_error_to_terminal(e)

                if 6 in output_options:    # Save SHP
                    try:
                        shp_name = os.path.join(output_folder, self.shp_file_entry.text())
                        shp_file = saveFile(shp_name, ".shp")
                        processed_plate_generator = shp_file.save_to_file(processed_plate_generator, time)
                        print("save to shp")
                        QMessageBox.about(self, "Success", f"SHP output saved to {os.path.basename(shp_name)}")
                    except Exception as e:
                        QMessageBox.warning(self, "An Error occurred:", str(e))
                        self.print_error_to_terminal(e)

                if 0 in output_options or 1 in output_options or 2 in output_options or 7 in output_options:  # Plot to Screen
                    # different file name
                    if 1 in output_options:
                        pdf_file = os.path.join(output_folder, self.pdf_file_entry.text())
                        pdf_file = os.path.splitext(pdf_file)[0]    # remove file extension, if any
                        if len(time_array) > 1:
                            self.save_fig["pdf"] = pdf_file + "_" + str(time)
                        else:
                            self.save_fig["pdf"] = pdf_file
                    if 7 in output_options:
                        svg_file = os.path.join(output_folder, self.svg_file_entry.text())
                        svg_file = os.path.splitext(svg_file)[0]
                        if len(time_array) > 1:
                            self.save_fig["svg"] = svg_file + "_" + str(time)
                        else:
                            self.save_fig["svg"] = svg_file

                    try:
                        figure.update_plot_vars(self.save_fig, time, self.map_title_edit.text(), self.get_raster_files())
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
                    mp4_file = os.path.join(output_folder, self.mp4_file_entry.text())
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
            step = abs((end - start) / 10.0)
        else:
            step = abs(float(step_text))
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

            if self.line_thickness_checkbox.isChecked():
                proj_kwargs["thin_lines"] = True
            else: proj_kwargs["thin_lines"] = False
            
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
            
            if projection_option in [1, 5]:  # Orthographic TransMerc
                # central coordinates
                proj_kwargs["center_lat"] = float(self.center_lat_entry.text())
                proj_kwargs["center_lon"] = float(self.center_lon_entry.text())
                print("collect center point")
            
            if projection_option in [7, 8]:  # AziEqui Stereo
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