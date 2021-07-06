from PyQt5.QtWidgets import QWidget, QAction, QToolBar, QApplication
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5 import QtGui
import qtawesome as qta
from forms.pdfpage import Ui_pagePDF
from const import *


class PDFPage(QWidget, Ui_pagePDF):
    def __init__(self, pixmap, index, label):
        super(PDFPage, self).__init__()
        self.setupUi(self)
        self.forminit()
        self.labelPixmap.setPixmap(pixmap)
        self.labelPageIndex.setText(label + ' ' + str(index + 1))
        self.id = index
        self.checked = False

    selected_page_signal = pyqtSignal(int)

    def mousePressEvent(self, event):
        self.selected_page_signal.emit(self.id)

    def setchecked(self, state):
        if state:
            self.labelpixmap_setstyle(CHECKED_BLUE_STYLE)
            self.checked = state
        else:
            self.labelpixmap_setstyle(NONE_STYLE)
            self.checked = state

    def labelpixmap_setstyle(self, style):
        if style == NONE_STYLE:
            self.labelPixmap.setStyleSheet("border: 0px solid blue;")
        elif style == CHECKED_BLUE_STYLE:
            self.labelPixmap.setStyleSheet("border: 1px solid blue;")
        else:
            pass


    def forminit(self):
        pass

    def __del__(self):
        self.labelPixmap.clear()
