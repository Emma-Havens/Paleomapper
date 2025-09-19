from PySide6.QtGui import QAction, QIcon, QFont
from PySide6.QtWidgets import (QLabel, QDialog, QVBoxLayout, QHBoxLayout, 
                               QSpacerItem, QSizePolicy, QTextBrowser, QAbstractScrollArea)
from PySide6.QtCore import Qt, QSize

def show_about_window():
    dialog = QDialog(None)
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
    
    dialog.setLayout(layout)
    dialog.exec()

def show_faq_window():
    dialog = QDialog(None)
    dialog.setSizeGripEnabled(True)
    dialog.resize(700, 600)
    dialog.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
    layout = QVBoxLayout()
    title = QLabel("PaleoMapper FAQ")
    title_font = title.font()
    title_font.setPointSize(40)
    title.setFont(title_font)
    layout.addWidget(title)

    text_browser = QTextBrowser()
    with open('faq.html', 'r') as faq:
        text_browser.setHtml(faq.read())

    # with open('faq.html', 'r') as faq:
    #     for paragraph in faq:
    #         body = QLabel(paragraph)
    #         body.setWordWrap(True)
    #         body.setTextFormat(Qt.RichText)
    #         print(body.sizeHint())
    #         body.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    #         layout.addWidget(body)
    
    text_browser.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
    layout.addWidget(text_browser)
    dialog.setLayout(layout)
    dialog.exec()

def show_color_options_window():
    pass