from forms.pdfpreview import Ui_dialogPDFPreview
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QApplication, QAbstractItemView
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
import qtawesome as qta
import os
import fitz
from pdfparser import PDFParser
from const import *


class dialogPDFPreview(QDialog, Ui_dialogPDFPreview):
    def __init__(self, type, filenames=None, pdfdoc=None, excludelist=None):
        super(dialogPDFPreview, self).__init__()
        self.setupUi(self)
        self.forminit()
        self.current_zoom = 0.5
        self.mode = type
        self.pdf_document = None
        self.pdf_documents = []
        self.image_list = []
        self.exclude = []
        if self.mode == DIALOG_MODE_PAGE:
            if filenames:
                self.pdf_document = PDFParser(os.path.normpath(filenames))
            self.setup_pagemode()
        elif self.mode == DIALOG_MODE_FILE:
            if filenames:
                for filename in filenames:
                    pdfdocument = PDFParser(os.path.normpath(filename))
                    self.pdf_documents.append(pdfdocument)
            self.setup_filemode()
        elif self.mode == DIALOG_MODE_MOVE:
            self.pdf_document = pdfdoc
            self.move_index = -1
            for item in excludelist:
                self.exclude.append(item.row())
            self.setup_movemode()
        elif self.mode == DIALOG_MODE_IMAGE:
            if filenames:
                for filename in filenames:
                    temp_tuple = (QPixmap(filename), os.path.normpath(filename))
                    self.image_list.append(temp_tuple)
                self.setup_filemode()
        elif self.mode == DIALOG_MODE_IMAGES:
            if filenames:
                for filename in filenames:
                    temp_tuple = (QPixmap(filename), os.path.normpath(filename))
                    self.image_list.append(temp_tuple)
                self.setup_image_mode()

    def forminit(self):
        self.pushButtonCancel.clicked.connect(self.reject)
        self.pushButtonAction.clicked.connect(self.accept)
        self.radioButtonAfter.toggled.connect(self.radiobutton_state)
        self.radioButtonBefore.toggled.connect(self.radiobutton_state)
        self.checkBoxAllPages.stateChanged.connect(self.allpages_checked)
        self.listWidgetPreview.itemSelectionChanged.connect(self.doc_pages_select)
        self.setMaximumHeight(500)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowSystemMenuHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('')
        self.setWindowIcon(qta.icon('mdi.file-pdf', color=COLOR_RED))

    def radiobutton_state(self, state):
        if self.radioButtonAfter.isChecked():
            self.radioButtonBefore.setChecked(False)
        elif self.radioButtonBefore.isChecked():
            self.radioButtonAfter.setChecked(False)

    def setup_pagemode(self):
        self.pushButtonAction.setEnabled(False)
        self.pushButtonMovePlus.setVisible(False)
        self.pushButtonMoveMinus.setVisible(False)
        self.labelMove.setVisible(False)
        self.setWindowTitle(QApplication.translate('CustomStrings',
                                                   'Choose pages to insert in your document and click Insert'))
        self.pushButtonAction.setText(QApplication.translate('CustomStrings', 'Insert'))
        self.pdfpages_paint()

    def setup_filemode(self):
        self.setWindowTitle(QApplication.translate('CustomStrings', 'Choose file order to merge and click Merge'))
        self.pushButtonAction.setText(QApplication.translate('CustomStrings', 'Merge'))
        self.pushButtonMovePlus.setEnabled(False)
        self.pushButtonMoveMinus.setEnabled(False)
        self.pushButtonMovePlus.clicked.connect(self.file_pagesmove_clicked)
        self.pushButtonMoveMinus.clicked.connect(self.file_pagesmove_clicked)
        self.labelInsert.setVisible(False)
        self.radioButtonBefore.setVisible(False)
        self.radioButtonAfter.setVisible(False)
        self.checkBoxAllPages.setVisible(False)
        self.listWidgetPreview.setSelectionMode(QAbstractItemView.SingleSelection)
        if self.mode == DIALOG_MODE_FILE:
            self.pdffiles_paint()
        elif self.mode == DIALOG_MODE_IMAGE:
            self.imagefiles_paint()

    def setup_image_mode(self):
        self.setWindowTitle(QApplication.translate('CustomStrings',
                                                   'Choose pages to insert in your document and click Insert'))
        self.pushButtonMovePlus.setEnabled(False)
        self.pushButtonMoveMinus.setEnabled(False)
        self.pushButtonAction.setText(QApplication.translate('CustomStrings', 'Insert'))
        self.pushButtonMovePlus.clicked.connect(self.file_pagesmove_clicked)
        self.pushButtonMoveMinus.clicked.connect(self.file_pagesmove_clicked)
        self.labelInsert.setVisible(False)
        self.radioButtonBefore.setVisible(True)
        self.radioButtonAfter.setVisible(True)
        self.checkBoxAllPages.setVisible(False)
        self.imagefiles_paint()

    def setup_movemode(self):
        self.pushButtonAction.setEnabled(False)
        self.pushButtonMovePlus.setVisible(False)
        self.pushButtonMoveMinus.setVisible(False)
        self.labelMove.setVisible(False)
        self.setWindowTitle(QApplication.translate('CustomStrings',
                                                        'Choose page to move your pages before or after'))
        self.pushButtonAction.setText(QApplication.translate('CustomStrings', 'Move'))
        self.listWidgetPreview.setSelectionMode(QAbstractItemView.SingleSelection)
        self.checkBoxAllPages.setVisible(False)
        self.pdfpages_paint()

    def file_pagesmove_clicked(self):
        target_index = -1
        if self.sender().objectName() == 'pushButtonMoveMinus':
            for index in self.listWidgetPreview.selectionModel().selectedIndexes():
                target_index = index.row()
                if target_index > 0:
                    target_index = target_index - 1
                if index.row() != target_index and self.mode == DIALOG_MODE_FILE:
                    self.pdf_documents.insert(target_index, self.pdf_documents.pop(index.row()))
                elif index.row() != target_index and self.mode == DIALOG_MODE_IMAGE or self.mode == DIALOG_MODE_IMAGES:
                    self.image_list.insert(target_index, self.image_list.pop(index.row()))
        elif self.sender().objectName() == 'pushButtonMovePlus':
            for index in self.listWidgetPreview.selectionModel().selectedIndexes():
                target_index = index.row()
                if target_index < self.listWidgetPreview.count() - 1:
                    target_index = target_index + 1
                if index.row() != target_index and self.mode == DIALOG_MODE_FILE:
                    self.pdf_documents.insert(target_index, self.pdf_documents.pop(index.row()))
                elif index.row() != target_index and self.mode == DIALOG_MODE_IMAGE or self.mode == DIALOG_MODE_IMAGES:
                    self.image_list.insert(target_index, self.image_list.pop(index.row()))
        if self.mode == DIALOG_MODE_FILE:
            self.pdffiles_paint()
        elif self.mode == DIALOG_MODE_IMAGE or self.mode == DIALOG_MODE_IMAGES:
            self.imagefiles_paint()

    def doc_pages_select(self):
        if self.mode == DIALOG_MODE_PAGE or self.mode == DIALOG_MODE_MOVE:
            if len(self.listWidgetPreview.selectionModel().selectedIndexes()) > 0:
                self.pushButtonAction.setEnabled(True)
                for item in self.listWidgetPreview.selectionModel().selectedIndexes():
                    self.move_index = item.row()
            else:
                self.pushButtonAction.setEnabled(False)
        elif self.mode == DIALOG_MODE_FILE or self.mode == DIALOG_MODE_IMAGE or self.mode == DIALOG_MODE_IMAGES:
            if len(self.listWidgetPreview.selectionModel().selectedIndexes()) > 0:
                self.pushButtonMovePlus.setEnabled(True)
                self.pushButtonMoveMinus.setEnabled(True)
            else:
                self.pushButtonMovePlus.setEnabled(False)
                self.pushButtonMoveMinus.setEnabled(False)

    def allpages_checked(self, state):
        for item in range(0, self.listWidgetPreview.count()):
            self.listWidgetPreview.item(item).setSelected(state)

    def pdfpages_paint(self):
        if self.mode != DIALOG_MODE_MOVE:
            self.pdf_document.render_pages(self.current_zoom)
        self.listWidgetPreview.setMinimumHeight(440)
        self.listWidgetPreview.setMaximumHeight(440)
        for index, page in enumerate(self.pdf_document.pdf_doc_pages):
            item = QListWidgetItem(QIcon(page), QApplication.translate('CustomStrings', 'Page') + ' ' + str(index + 1))
            if index in self.exclude:
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.listWidgetPreview.addItem(item)

    def pdffiles_paint(self):
        self.listWidgetPreview.setMinimumHeight(440)
        self.listWidgetPreview.setMaximumHeight(440)
        self.listWidgetPreview.clear()
        for doc in self.pdf_documents:
            item = QListWidgetItem(QIcon(doc.get_page(0, self.current_zoom)), doc.current_file_name_short + '.pdf')
            self.listWidgetPreview.addItem(item)

    def imagefiles_paint(self):
        self.listWidgetPreview.setMinimumHeight(440)
        self.listWidgetPreview.setMaximumHeight(440)
        self.listWidgetPreview.clear()
        for image in self.image_list:
            item = QListWidgetItem(QIcon(image[0]), image[1])
            self.listWidgetPreview.addItem(item)

    def __del__(self):
        if self.mode != DIALOG_MODE_MOVE:
            if self.pdf_documents and len(self.pdf_documents) > 0:
                for doc in self.pdf_documents:
                    doc.close_file()
            elif self.pdf_document:
                self.pdf_document.close_file()
