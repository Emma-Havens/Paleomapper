from PySide6.QtWidgets import (
    QStyledItemDelegate, QApplication, QStyle, QStyleOptionButton, QStyleOption
    )
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QEvent, QRect, QSize
from PySide6.QtGui import QPainter, QPen, QBrush
import os.path
import glob
import sys
import json

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
    def __init__(self, input_dir="input", parent=None):
        super().__init__(parent)
        self.files = []  # Each item is [checked, arrows, path, param1, param2]
        self.headers = ["", "", "File Path", "Border Color", "Fill Color"]
        self.file_index = 2
        self.rot_file = ""

        self.upload_files(input_dir)
              
    def upload_files(self, input_dir):
        if getattr(sys, 'frozen', False):
            exec_dir = os.path.dirname(sys.executable)
            input_dir = exec_dir + "/" + input_dir
            print(input_dir)
        
        if not os.path.isdir(input_dir):
            return

        files_to_add = []
        proj_file = None
        files = glob.iglob(input_dir + '/**/*.*', recursive=True)
        print("Adding files:")
        for file in files:
            # print(file)
            if os.path.splitext(file)[1] in [".gpml", ".dat", ".csv"]:
                files_to_add.append(file)
            elif os.path.splitext(file)[1] == ".json":
                proj_file = file
            elif os.path.splitext(file)[1] == ".rot":
                self.rot_file = file
                print("rot found")

        if proj_file: self.change_project_file(proj_file)
        
        # add files not defined by a project
        for file in files_to_add:
            bool_array = [ loaded_file[self.file_index] == file for loaded_file in self.files ]
            print(bool_array)
            if not True in bool_array:
                self.add_file(file, False)
                print(f"added file {file}")
            else:
                print(f"skipping file {file}")
    
    def change_project_file(self, proj_file):
        # remove all current files
        num_files = len(self.files)
        for _ in range(num_files):
            self.remove_row(0)

        # add files in project file
        file_list = json.load(open(proj_file, 'r'))
        
        for file in file_list:
            json_path = os.path.dirname(proj_file)
            file_path = json_path + "/" + file["file"]
            try:
                # add files defined in project to gui
                self.add_file(file_path, file["checked"], file["bcolor"], file["fcolor"])
                json_file = file["file"]
                print(f"in project: {json_file}")

            except FileNotFoundError:
                print(f"Could not find {file_path}")
                continue
    
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
    
    def add_file(self, file_path, checked=True, border_color="black", fill_color=""):
        if not os.path.exists(file_path):
            raise FileNotFoundError
        
        self.beginInsertRows(QModelIndex(), len(self.files), len(self.files))
        extension = os.path.splitext(file_path)[1]
        if extension == ".csv":
            border_color = fill_color = "infile" 
        self.files.insert(0, [checked, False, file_path, border_color, fill_color])
        self.endInsertRows()
    
    def remove_row(self, row):
        if 0 <= row < len(self.files):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.files[row]
            self.endRemoveRows()
    
    def get_selected_files(self):
        """Returns list of checked file paths"""
        return [file[1] for file in self.files if file[0]]
    
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