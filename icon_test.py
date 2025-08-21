import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar, QLabel
from PySide6.QtGui import QIcon


class IconWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Icon Window")

        # Create status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Add an icon to the status bar
        pm_icon_light = QIcon('PM_icon_lightbg.png')
        pm_icon_dark = QIcon('PM_icon_darkbg.png')

        icon_light = QLabel()
        icon_light.setPixmap(pm_icon_light.pixmap(25, 25))
        icon_dark = QLabel()
        icon_dark.setPixmap(pm_icon_dark.pixmap(25, 25))

        # Add the icon to the status bar (left side)
        status_bar.addPermanentWidget(icon_light)
        status_bar.addPermanentWidget(icon_dark)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pm_icon = QIcon('PM_icon_darkbg.png')
    app.setWindowIcon(pm_icon)

    from gui import PlateTrackerApp
    window = PlateTrackerApp()
    window.show()
    sys.exit(app.exec())