from PySide6.QtWidgets import (
    QStyledItemDelegate, QApplication, QStyle, QStyleOptionButton, QStyleOption, QMessageBox
    )
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QEvent, QRect, QSize
from PySide6.QtGui import QPainter
import os.path
import glob
import sys
import json
import shutil

class ArrowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_size = 18
        self.margin = 6
        self.spacing = 6

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate positions - side by side but with up/down arrows
        total_width = 2 * self.button_size + self.spacing
        start_x = option.rect.center().x() - total_width // 2
        
        # Up arrow (left position)
        up_rect = QRect(
            start_x,
            option.rect.center().y() - self.button_size // 2,
            self.button_size,
            self.button_size
        )
        
        # Down arrow (right position)
        down_rect = QRect(
            start_x + self.button_size + self.spacing,
            option.rect.center().y() - self.button_size // 2,
            self.button_size,
            self.button_size
        )
        
        # Draw up arrow (points up)
        self.draw_arrow(painter, up_rect, QStyle.PE_IndicatorArrowUp)
        
        # Draw down arrow (points down)
        self.draw_arrow(painter, down_rect, QStyle.PE_IndicatorArrowDown)
        
        painter.restore()
    
    def draw_arrow(self, painter, rect, arrow_type):
        # Draw arrow
        arrow = QStyleOption()
        arrow.rect = rect.adjusted(3, 3, -3, -3)
        QApplication.style().drawPrimitive(arrow_type, arrow, painter)
    
    def editorEvent(self, event, model, option, index):
        if not index.isValid():  # Critical check
            return False
            
        # Calculate positions (same as paint())
        total_width = 2 * self.button_size + self.spacing
        start_x = option.rect.center().x() - total_width // 2
        
        up_rect = QRect(
            start_x,
            option.rect.center().y() - self.button_size // 2,
            self.button_size,
            self.button_size
        )
        
        down_rect = QRect(
            start_x + self.button_size + self.spacing,
            option.rect.center().y() - self.button_size // 2,
            self.button_size,
            self.button_size
        )
        
        pos = event.pos()
        
        # Handle clicks
        if (event.type() == QEvent.MouseButtonRelease and 
              event.button() == Qt.LeftButton):
            
            try:
                if up_rect.contains(pos) and index.row() > 0:
                    model.move_row(index.row(), index.row() - 1)
                    return True
                elif down_rect.contains(pos) and index.row() < model.rowCount() - 1:
                    model.move_row(index.row(), index.row() + 1)
                    return True
            except Exception as e:
                print(f"Move row failed: {e}")
                return False
        
        return False
    
    def sizeHint(self, option, index):
        return QSize(2 * (self.button_size + self.margin) + self.spacing,
                    self.button_size + 2 * self.margin)

class CheckBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
            super().__init__(parent)

    def createEditor(self, parent, option, index):
        # No editor needed - we'll handle clicks directly
        return None

    def paint(self, painter, option, index):
        if not index.isValid():  # MUST CHECK
            return
            
        painter.save()  # CRITICAL
        try:
            # Draw the checkbox centered in the cell
            checked = index.data(Qt.CheckStateRole) == Qt.Checked
            checkbox_style = option.widget.style() if option.widget else QApplication.style()
            checkbox_rect = checkbox_style.subElementRect(QStyle.SE_CheckBoxIndicator, option, option.widget)
            checkbox_rect.moveCenter(option.rect.center())
            
            checkbox_option = QStyleOptionButton()
            checkbox_option.rect = checkbox_rect
            checkbox_option.state = QStyle.State_Enabled
            if checked:
                checkbox_option.state |= QStyle.State_On
            else:
                checkbox_option.state |= QStyle.State_Off
                
            checkbox_style.drawControl(QStyle.CE_CheckBox, checkbox_option, painter)
        finally:
            painter.restore()  # GUARANTEES cleanup

    def editorEvent(self, event, model, option, index):
        # Check if this is a left mouse button release event
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            # Toggle checkbox state
            checked = index.data(Qt.CheckStateRole) != Qt.Checked
            model.setData(index, Qt.Checked if checked else Qt.Unchecked, Qt.CheckStateRole)
            return True
        return False

class FileTableModel(QAbstractTableModel):
    def __init__(self, raster_table, proj_path, parent=None):
        super().__init__(parent)
        self.raster_table = raster_table
        self.accepted_extensions = [".dat", ".gpml", ".csv", ".shp"]
        self.files = []  # Each item is [checked, arrows, path, bcolor, fcolor, alpha]
        self.headers = ["", "", "File Path", "Border Color", "Fill Color", "Alpha"]
        self.file_index = 2
        self.rot_file = ""
        self.proj_file = ""

        if os.path.exists(proj_path): self.load_project(proj_path)
              
    def upload_files(self, input_dir):
        if getattr(sys, 'frozen', False):
            exec_dir = os.path.dirname(sys.executable)
            input_dir = os.path.join(exec_dir, input_dir)
            print(input_dir)
        
        if not os.path.isdir(input_dir):
            return

        all_extensions = self.accepted_extensions + self.raster_table.accepted_extensions
        files_to_add = []
        files = glob.iglob(input_dir + '/**/*.*', recursive=True)
        print("Adding files:")
        for file in files:
            # print(file)
            if os.path.splitext(file)[1] in all_extensions:
                files_to_add.append(file)
            elif os.path.splitext(file)[1] == ".json":
                self.proj_file = file
            elif os.path.splitext(file)[1] == ".rot":
                self.rot_file = file
                # print("rot found")

        if os.path.exists(self.proj_file): self.load_project(self.proj_file)
        
        # add files not defined by a project
        all_files = self.files + self.raster_table.files
        for file in files_to_add:
            bool_array = [ loaded_file[self.file_index] == file for loaded_file in all_files ]
            # print(bool_array)
            if not True in bool_array:
                if os.path.splitext(file)[1] in self.accepted_extensions:
                    self.add_file(file, False)
                else:
                    self.raster_table.add_file(file, False)
    
    def load_project(self, proj_path):
        self.proj_file = proj_path

        # remove all current files
        num_files = len(self.files)
        for _ in range(num_files):
            self.remove_row(0)
        num_raster = len(self.raster_table.files)
        for _ in range(num_raster):
            self.raster_table.remove_row(0)
        self.rot_file = ""

        # add files in project file
        file_list = json.load(open(self.proj_file, 'r'))
        
        for file in file_list:
            json_path = os.path.dirname(self.proj_file)
            file_path = os.path.join(json_path, file["file"])
            try:
                # add rot file in project to gui
                if os.path.splitext(file_path)[1] == ".rot":
                    if os.path.exists(file_path):
                        self.rot_file = file_path
                    continue

                # add files defined in project to gui
                if os.path.splitext(file_path)[1] in self.accepted_extensions:
                    self.add_file(file_path, file["checked"], file["bcolor"], file["fcolor"], file["alpha"])
                elif os.path.splitext(file_path)[1] in self.raster_table.accepted_extensions:
                    self.raster_table.add_file(file_path, file["checked"], file["extent"], file["alpha"])


            except FileNotFoundError:
                print(f"Could not find {file_path}")
                continue

    def save_project(self, proj_path, save_to_current=False):
        if not save_to_current:
            self.proj_file = proj_path

        files_to_write = self.files.copy() + self.raster_table.files.copy()
        files_to_write.reverse()
        dict = []
        if self.rot_file:
            dict.append({"file": os.path.basename(self.rot_file)})
        for file in files_to_write:
            entry = {}
            entry["file"] = os.path.basename(file[self.file_index])
            entry["checked"] = file[0]
            if os.path.splitext(file[self.file_index])[1] in self.accepted_extensions:
                entry["bcolor"] = file[3]
                entry["fcolor"] = file[4]
                entry["alpha"] = file[5]
            else:
                entry["extent"] = file[3]
                entry["alpha"] = file[4]
            dict.append(entry)

        with open(self.proj_file, 'w') as outfile:
            json.dump(dict, outfile, indent=4)

        files_to_save = ([ file[self.file_index] for file in self.files ] + 
                         [ file[self.raster_table.file_index] for file in self.raster_table.files])
        files_to_save.append(self.rot_file)
        # print(files_to_save)
        
        for source_file in files_to_save:
            dest_file = os.path.join(os.path.dirname(self.proj_file), os.path.basename(source_file))            
            if not os.path.exists(dest_file):
                shutil.copy2(source_file, dest_file)

        self.load_project(self.proj_file)

    def get_proj_name(self):
        return os.path.splitext(os.path.basename(self.proj_file))[0]
    
    def rowCount(self, parent=None):
        return len(self.files)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        row, col = index.row(), index.column()
        
        if col == 0:    # Checkbox column
            if role == Qt.CheckStateRole:
                return Qt.Checked if self.files[row][0] else Qt.Unchecked
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        elif col == 1:    # Arrow column
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            return None
        elif col == 2:      # File path column
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return os.path.basename(self.files[row][2])
        elif col == 5:  # Alpha columns
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return str(self.files[row][col])
        else:  # Other columns
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self.files[row][col]
        
        return None
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
            
        row, col = index.row(), index.column()
        
        if col == 0 and role == Qt.CheckStateRole:
            self.files[row][0] = value == Qt.Checked
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        elif col == 1:
            return False
        elif role == Qt.EditRole and col == 5:
            try: 
                if value == "infile": self.files[row][col] = value
                else: self.files[row][col] = float(value)
            except ValueError: return False
            self.dataChanged.emit(index, index)
            return True
        elif role == Qt.EditRole and col > 0:
            self.files[row][col] = value
            self.dataChanged.emit(index, index)
            return True
            
        return False
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
    
    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 0:  # Checkbox column
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        elif index.column() == 1:   # Arrow column
            flags |= Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:  # Other columns
            flags |= Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return flags
    
    def add_file(self, file_path, checked=True, border_color="default", fill_color="default", alpha=-1.0):
        if not os.path.exists(file_path):
            raise FileNotFoundError
        extension = os.path.splitext(file_path)[1]
        if border_color == "default":
            if extension == ".csv": border_color = "infile" 
            else: border_color = "black"
        if fill_color == "default":
            if extension == ".csv": fill_color = "infile" 
            else: fill_color = ""
        if alpha == -1.0:
            if extension == ".csv": alpha = "infile"
            else: alpha = 1.0
        self.beginInsertRows(QModelIndex(), len(self.files), len(self.files))
        self.files.insert(0, [checked, False, file_path, border_color, fill_color, alpha])
        self.endInsertRows()
    
    def remove_row(self, row):
        if 0 <= row < len(self.files):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.files[row]
            self.endRemoveRows()
    
    def get_selected_files(self):
        return [file[self.file_index] for file in self.files if file[0]]
    
    def move_row(self, from_row, to_row):
        """Robust row moving with proper destination adjustment"""
        row_count = len(self.files)
        
        # Validate indices
        if not (0 <= from_row < row_count and 0 <= to_row <= row_count):
            print(f"Invalid move: {from_row}->{to_row} (max {row_count})")
            return False
            
        if from_row == to_row:
            return True  # No-op
            
        # Calculate adjusted destination
        adjusted_to = to_row
        if to_row > from_row:
            adjusted_to += 1
            
        try:
            if not self.beginMoveRows(QModelIndex(), from_row, from_row,
                                    QModelIndex(), adjusted_to):
                print("beginMoveRows returned False")
                return False
                
            # Perform the move
            row_data = self.files.pop(from_row)
            self.files.insert(to_row, row_data)
            
            self.endMoveRows()
            return True
        except Exception as e:
            print(f"Move failed: {e}")
            return False
    
class RasterTableModel(QAbstractTableModel):
    def __init__(self, input_dir="input", parent=None):
        super().__init__(parent)
        self.accepted_extensions = [".jpg", ".jpeg", ".png"]
        self.files = []  # Each item is [checked, arrows, path, [w,e,s,n], alpha]
        self.headers = ["", "", "File Path", "Extent", "Alpha"]
        self.file_index = 2

    def rowCount(self, parent=None):
        return len(self.files)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        row, col = index.row(), index.column()
        
        if col == 0:    # Checkbox column
            if role == Qt.CheckStateRole:
                return Qt.Checked if self.files[row][0] else Qt.Unchecked
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        elif col == 1:    # Arrow column
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            return None
        elif col == 2:  # File path column
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return os.path.basename(self.files[row][2])
        elif col == 3:  # Extent column
            if role == Qt.DisplayRole or role == Qt.EditRole:
                extent_string = ""
                for el in self.files[row][col]: extent_string += str(el) + ','
                return extent_string[:-1]
        else:           # Alpha columns
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return str(self.files[row][col])
        
        return None
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
            
        row, col = index.row(), index.column()
        
        if col == 0 and role == Qt.CheckStateRole:  # Checkbox column
            self.files[row][0] = value == Qt.Checked
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        elif col == 1:                              # Arrow column
            return False
        elif role == Qt.EditRole and col == 2:      # File Path column
            self.files[row][col] = value
            self.dataChanged.emit(index, index)
            return True
        elif role == Qt.EditRole and col == 3:      # Extent column
            extent = [ int(el.strip()) for el in value.split(',') ]
            if len(extent) == 4:
                self.files[row][col] = extent
            else:
                print(f"Incorrect extent entered: {value}")
                return False
            self.dataChanged.emit(index, index)
            return True
        elif role == Qt.EditRole and col == 4:      # Alpha column
            try: self.files[row][col] = float(value)
            except ValueError: return False
            self.dataChanged.emit(index, index)
            return True
            
        return False
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
    
    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 0:  # Checkbox column
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        elif index.column() == 1:   # Arrow column
            flags |= Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:  # Other columns
            flags |= Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return flags
    
    def add_file(self, file_path, checked=True, extent=[-180,180,-90,90], alpha=1.0):
        if not os.path.exists(file_path):
            raise FileNotFoundError
        
        self.beginInsertRows(QModelIndex(), len(self.files), len(self.files))
        self.files.insert(0, [checked, False, file_path, extent, alpha])
        self.endInsertRows()
    
    def remove_row(self, row):
        if 0 <= row < len(self.files):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.files[row]
            self.endRemoveRows()
    
    def get_selected_files(self):
        return [file[self.file_index] for file in self.files if file[0]]
    
    def move_row(self, from_row, to_row):
        row_count = len(self.files)
        
        # Validate indices
        if not (0 <= from_row < row_count and 0 <= to_row <= row_count):
            print(f"Invalid move: {from_row}->{to_row} (max {row_count})")
            return False
            
        if from_row == to_row:
            return True  # No-op
            
        # Calculate adjusted destination
        adjusted_to = to_row
        if to_row > from_row:
            adjusted_to += 1
            
        try:
            if not self.beginMoveRows(QModelIndex(), from_row, from_row,
                                    QModelIndex(), adjusted_to):
                print("beginMoveRows returned False")
                return False
                
            # Perform the move
            row_data = self.files.pop(from_row)
            self.files.insert(to_row, row_data)
            
            self.endMoveRows()
            return True
        except Exception as e:
            print(f"Move failed: {e}")
            return False