from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QLabel, QDialog, QVBoxLayout, QHBoxLayout, 
                               QSpacerItem, QSizePolicy, QTextBrowser, QAbstractScrollArea)

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

import math

class AboutDialog:
    def __init__(self):
        self.dialog = QDialog(None)
        layout = QVBoxLayout()
        header = QHBoxLayout()

        pm_icon_light = QIcon('ai_owl_logo.png')
        icon_light = QLabel()
        icon_light.setPixmap(pm_icon_light.pixmap(50, 50))
        title = QLabel("PaleoMapper")
        title_font = title.font()
        title_font.setPointSize(40)
        title.setFont(title_font)
        header.addWidget(icon_light)
        header.addSpacerItem(QSpacerItem(20, 1))
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        with open('About.txt', 'r') as abt:
            for paragraph in abt:
                body = QLabel(paragraph)
                body.setWordWrap(True)
                layout.addWidget(body)
        
        self.dialog.setLayout(layout)

    def show_window(self):
        self.dialog.show()

class FAQDialog:
    def __init__(self):
        self.dialog = QDialog(None)
        self.dialog.setSizeGripEnabled(True)
        self.dialog.resize(700, 600)
        self.dialog.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout()
        title = QLabel("PaleoMapper FAQ")
        title_font = title.font()
        title_font.setPointSize(40)
        title.setFont(title_font)
        layout.addWidget(title)

        text_browser = QTextBrowser()
        with open('faq.html', 'r') as faq:
            text_browser.setHtml(faq.read())
        
        text_browser.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        layout.addWidget(text_browser)
        self.dialog.setLayout(layout)

    def show_window(self):
        self.dialog.show()

class ColorDialog:
    def __init__(self):
        self.dialog = QDialog(None)
        self.dialog.setSizeGripEnabled(True)
        self.dialog.resize(900, 900)
        layout = QVBoxLayout()
        title = QLabel("Color Options")
        title_font = title.font()
        title_font.setPointSize(40)
        title.setFont(title_font)
        layout.addWidget(title)
        preamble = QLabel("The following are key words that can be used as border and fill colors. " \
                "Paleomapper can also utilize any formats allowed by Matplotlib, aside from RGB tuples (see " \
                "the \"Specifying Colors\" tutorial at matplotlib.org for more information). Notably, this includes " \
                "hexcode RGB (#0f0f0f) and 'none'.")
        preamble.setWordWrap(True)
        layout.addWidget(preamble)
        
        cell_width = 100
        cell_height = 22
        swatch_width = 18
        margin = 12
        ncols = 4
        colors = mcolors.CSS4_COLORS

        names = sorted(colors, key=lambda c: tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(c))))
        n = len(names)
        nrows = math.ceil(n / ncols)
        width = cell_width * ncols + 2 * margin
        height = cell_height * nrows + 2 * margin

        qtfig = FigureCanvas(Figure(figsize=(width, height)))
        ax = qtfig.figure.subplots()

        qtfig.figure.subplots_adjust(margin/width, margin/height,
                            (width-margin)/width, (height-margin)/height)
        ax.set_xlim(0, cell_width * ncols)
        ax.set_ylim(cell_height * (nrows-0.5), -cell_height/2.)
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)
        ax.set_axis_off()

        for i, name in enumerate(names):
            row = i % nrows
            col = i // nrows
            y = row * cell_height

            swatch_start_x = cell_width * col
            text_pos_x = cell_width * col + swatch_width + 7

            ax.text(text_pos_x, y, name, fontsize=10,
                    horizontalalignment='left',
                    verticalalignment='center')

            ax.add_patch(
                Rectangle(xy=(swatch_start_x, y-9), width=swatch_width,
                        height=18, facecolor=colors[name], edgecolor='0.7')
            )
        
        layout.addWidget(qtfig)
        layout.addWidget(QLabel("<strong>Additional keywords:</strong>"))
        multicolor = QLabel("multicolor = assign each unit a random color from the above table " \
        "(not including overly light colors)")
        multicolor.setWordWrap(True)
        layout.addWidget(multicolor)
        byOceanAge = QLabel("byOceanAge = assign each unit a ROYGBIV color according to its age (0-250Ma)")
        byOceanAge.setWordWrap(True)
        layout.addWidget(byOceanAge)
        byGeoAge = QLabel("byGeoAge = assign each unit a color from the International Chronostratigraphic Chart " \
        "according to its age (0-4567Ma)")
        byGeoAge.setWordWrap(True)
        layout.addWidget(byGeoAge)
        byPlateId = QLabel("byPlateId = assign each unit a color according to the leading digit of the unit's " \
        "plate id (hue) and the last digit of the unit's plate id (lightness)")
        byPlateId.setWordWrap(True)
        layout.addWidget(byPlateId)
        infile = QLabel("infile = the color that is specified within the data file will be used for plotting (only" \
        " available for data files where color can be specified for units; includes the keywords specified above)")
        infile.setWordWrap(True)
        layout.addWidget(infile)

        self.dialog.setLayout(layout)

    def show_window(self):
        self.dialog.show()

def show_preferences_window():
    dialog = QDialog(None)
    dialog.setSizeGripEnabled(True)
    layout = QVBoxLayout()
    title = QLabel("Preferences")
    title_font = title.font()
    title_font.setPointSize(40)
    title.setFont(title_font)
    layout.addWidget(title)

    
    
    dialog.setLayout(layout)
    dialog.exec()