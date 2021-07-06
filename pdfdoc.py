from pdfparser import *
from PyQt5.QtWidgets import QAction, QToolBar, QLabel, QApplication, QListWidgetItem, QFileDialog, QTabBar, \
    QCheckBox, QMessageBox, QSpinBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QSize
import qtawesome as qta
from forms.pdfdoctab import Ui_tabPDFDoc
from pdfpreview import dialogPDFPreview
from pdfpage import PDFPage
from pdfcompress import PDFCompress
from const import *


class PDFDoc(QTabBar, Ui_tabPDFDoc):
    def __init__(self, filename=None):
        super(PDFDoc, self).__init__()
        self.setupUi(self)
        self.forminit()
        self.current_zoom = 1.0
        if filename:
            self.pdf_document = PDFParser(filename)
            if self.pdf_document.error_code > 0:
                self.show_error_message()
                self.close()
            else:
                self.pdfpages_paint()

    saveas_signal = pyqtSignal(str)

    def pdfpages_paint(self):
        self.pdf_document.render_pages(self.current_zoom)
        current_pages_quantity = self.verticalLayoutPDF.count()
        if current_pages_quantity > 0:
            self.listWidgetPages.clear()
            for index in range(0, current_pages_quantity):
                item = self.verticalLayoutPDF.itemAt(index).widget()
                item.deleteLater()
        for index, page in enumerate(self.pdf_document.pdf_doc_pages):
            pdfpage = PDFPage(page, index, QApplication.translate('CustomStrings', 'Page'))
            pdfpage.selected_page_signal.connect(self.pdfpage_clicked)
            self.verticalLayoutPDF.addWidget(pdfpage)
            item = QListWidgetItem(qta.icon('mdi.file-pdf-outline', color = COLOR_BLUE, color_active=COLOR_RED),
                                                         QApplication.translate('CustomStrings', 'Page') + ' ' +
                                                         str(index + 1))
            item.setSizeHint(QSize(self.listWidgetPages.width(), 64))
            self.listWidgetPages.addItem(item)

    @pyqtSlot(int)
    def pdfpage_clicked(self, value):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if self.verticalLayoutPDF.itemAt(value).widget().checked:
                self.listWidgetPages.item(value).setSelected(False)
                self.verticalLayoutPDF.itemAt(value).widget().setchecked(False)
            else:
                self.listWidgetPages.item(value).setSelected(True)
                self.verticalLayoutPDF.itemAt(value).widget().setchecked(True)
        else:
            for index in range(0, self.verticalLayoutPDF.count()):
                self.verticalLayoutPDF.itemAt(index).widget().setchecked(False)
                self.listWidgetPages.item(index).setSelected(False)
            self.verticalLayoutPDF.itemAt(value).widget().setchecked(True)
            self.listWidgetPages.item(value).setSelected(True)

    def forminit(self):
        self.save_action = QAction(qta.icon('mdi.content-save-outline', color=COLOR_BLUE),
                                   QApplication.translate('CustomStrings', 'Save'))
        self.save_action.triggered.connect(self.doc_save)
        self.save_action.setEnabled(False)
        self.saveas_action = QAction(qta.icon('mdi.content-save-edit-outline', color=COLOR_BLUE),
                                     QApplication.translate('CustomStrings', 'Save As'))
        self.saveas_action.triggered.connect(self.doc_saveas)
        self.zoom_in_action = QAction(qta.icon('mdi.magnify-plus-outline'),
                                      QApplication.translate('CustomStrings', 'Zoom in'))
        self.zoom_in_action.triggered.connect(self.doc_zoom_in)
        self.zoom_out_action = QAction(qta.icon('mdi.magnify-minus-outline'),
                                       QApplication.translate('CustomStrings', 'Zoom out'))
        self.zoom_out_action.triggered.connect(self.doc_zoom_out)
        self.zoom_label = QLabel('100%')
        self.dummy_action = QLabel(QApplication.translate('CustomStrings', 'Page actions'))
        self.dummy_action2 = QLabel(QApplication.translate('CustomStrings', 'Document actions'))
        self.delete_action = QAction(qta.icon('mdi.delete-outline', color=COLOR_RED),
                                     QApplication.translate('CustomStrings', 'Delete'))
        self.delete_action.triggered.connect(self.doc_pages_delete)
        self.delete_action.setEnabled(False)
        self.rotate_cw_action = QAction(qta.icon('mdi.rotate-right'),
                                        QApplication.translate('CustomStrings', 'Rotate CW'))
        self.rotate_cw_action.triggered.connect(self.doc_pages_rotate_cw)
        self.rotate_cw_action.setEnabled(False)
        self.rotate_ccw_action = QAction(qta.icon('mdi.rotate-left'),
                                         QApplication.translate('CustomStrings', 'Rotate CCW'))
        self.rotate_ccw_action.triggered.connect(self.doc_pages_rotate_ccw)
        self.rotate_ccw_action.setEnabled(False)
        self.extract_action = QAction(qta.icon('mdi.file-download-outline'),
                                      QApplication.translate('CustomStrings', 'Pages extract'))
        self.extract_action.triggered.connect(self.doc_pages_extract)
        self.extract_action.setEnabled(False)
        self.insert_action = QAction(qta.icon('mdi.file-upload-outline'),
                                     QApplication.translate('CustomStrings', 'Pages insert'))
        self.insert_action.triggered.connect(self.doc_pages_insert)
        self.insert_action.setEnabled(False)
        self.insert_images_action = QAction(qta.icon('mdi.file-image-outline'),
                                     QApplication.translate('CustomStrings', 'Images insert'))
        self.insert_images_action.triggered.connect(self.doc_images_insert)
        self.insert_images_action.setEnabled(False)
        self.move_action = QAction(qta.icon('mdi.file-move-outline'),
                                   QApplication.translate('CustomStrings', 'Move pages'))
        self.move_action.triggered.connect(self.doc_pages_move)
        self.move_action.setEnabled(False)
        self.pagenumber_action = QAction(qta.icon('mdi.numeric-1-box-multiple-outline'),
                                         QApplication.translate('CustomStrings', 'Insert page number'))
        self.pagenumber_action.triggered.connect(self.doc_pages_number_insert)
        self.pagenumber_action.setEnabled(False)
        self.compress_action = QAction(qta.icon('mdi.buffer'),
                                       QApplication.translate('CustomStrings', 'Compress document'))
        self.compress_action.triggered.connect(self.doc_compress)
        self.close_action = QAction(qta.icon('mdi.close-box-outline', color=COLOR_RED),
                                    QApplication.translate('CustomStrings', 'Close document'))
        self.close_action.triggered.connect(self.close_tab)
        self.spinBoxCompression = QSpinBox()
        self.spinBoxCompression.setMinimum(0)
        self.spinBoxCompression.setMaximum(4)
        self.spinBoxCompression.setValue(DEFAULT_COMPRESS_LEVEL)

        self.upRightToolBar = QToolBar()
        self.upRightToolBar.setMovable(True)
        self.upRightToolBar.addWidget(self.dummy_action2)
        self.upRightToolBar.addAction(self.zoom_in_action)
        self.upRightToolBar.addWidget(self.zoom_label)
        self.upRightToolBar.addAction(self.zoom_out_action)
        self.upRightToolBar.addWidget(self.spinBoxCompression)
        self.upRightToolBar.addAction(self.compress_action)
        self.upRightToolBar.addAction(self.save_action)
        self.upRightToolBar.addAction(self.saveas_action)
        self.upRightToolBar.addAction(self.close_action)

        self.upLeftToolBar = QToolBar()
        self.upLeftToolBar.addWidget(self.dummy_action)
        self.upLeftToolBar.addAction(self.rotate_ccw_action)
        self.upLeftToolBar.addAction(self.rotate_cw_action)
        self.upLeftToolBar.addAction(self.delete_action)
        self.upLeftToolBar.addAction(self.extract_action)
        self.upLeftToolBar.addAction(self.insert_action)
        self.upLeftToolBar.addAction(self.insert_images_action)
        self.upLeftToolBar.addAction(self.move_action)
        self.upLeftToolBar.addAction(self.pagenumber_action)

        self.horizontalLayoutToolBar.addStretch()
        self.horizontalLayoutToolBar.addWidget(self.upLeftToolBar)
        self.horizontalLayoutToolBar.addStretch()
        self.horizontalLayoutToolBar.addWidget(self.upRightToolBar)
        self.horizontalLayoutToolBar.addStretch()

        self.dummyToolBar = QToolBar()
        self.dummyaction = QAction(qta.icon('mdi.file-document-multiple-outline'), '')
        self.dummyaction.setEnabled(False)
        self.checkBoxAllPages = QCheckBox(QApplication.translate('CustomStrings', 'Select all pages'))
        self.checkBoxAllPages.stateChanged.connect(self.allpages_selected)
        self.dummyToolBar.addAction(self.dummyaction)
        self.dummyToolBar.addWidget(self.checkBoxAllPages)
        widget = self.verticalLayoutLeft.itemAt(0).widget()
        self.verticalLayoutLeft.addWidget(self.dummyToolBar)
        self.verticalLayoutLeft.addWidget(widget)

        self.listWidgetPages.itemSelectionChanged.connect(self.doc_pages_select)

    def allpages_selected(self, state):
        for index in range(0, self.verticalLayoutPDF.count()):
            self.verticalLayoutPDF.itemAt(index).widget().setchecked(state)
        for item in range(0, self.listWidgetPages.count()):
            self.listWidgetPages.item(item).setSelected(state)

    @pyqtSlot()
    def retranslate(self):
        self.save_action.setText(QApplication.translate('CustomStrings', 'Save'))
        self.zoom_in_action.setText(QApplication.translate('CustomStrings', 'Zoom in'))
        self.zoom_out_action.setText(QApplication.translate('CustomStrings', 'Zoom out'))
        self.dummy_action.setText(QApplication.translate('CustomStrings', 'Page actions'))
        self.dummy_action2.setText(QApplication.translate('CustomStrings', 'Document actions'))
        self.delete_action.setText(QApplication.translate('CustomStrings', 'Delete'))
        self.rotate_cw_action.setText(QApplication.translate('CustomStrings', 'Rotate CW'))
        self.rotate_ccw_action.setText(QApplication.translate('CustomStrings', 'Rotate CCW'))
        self.extract_action.setText(QApplication.translate('CustomStrings', 'Pages extract'))
        self.insert_action.setText(QApplication.translate('CustomStrings', 'Pages insert'))
        self.move_action.setText(QApplication.translate('CustomStrings', 'Move pages'))
        self.pagenumber_action.setText(QApplication.translate('CustomStrings', 'Insert page number'))
        self.compress_action.setText(QApplication.translate('CustomStrings', 'Compress document'))
        self.close_action.setText(QApplication.translate('CustomStrings', 'Close document'))
        self.checkBoxAllPages.setText(QApplication.translate('CustomStrings', 'Select all pages'))
        for index in range(0, self.listWidgetPages.count()):
            self.listWidgetPages.item(index).setText(QApplication.translate('CustomStrings', 'Page') + ' ' +
                                                     str(index + 1))
            self.verticalLayoutPDF.itemAt(index).widget().labelPageIndex.setText(QApplication.translate('CustomStrings', 'Page')
                                                                                 + ' ' + str(index + 1))

    def doc_save(self):
        self.pdf_document.save_doc()
        self.save_action.setEnabled(False)

    def doc_saveas(self):
        filename = QFileDialog.getSaveFileName(self, QApplication.translate('CustomStrings', 'Save PDF file'),
                                               directory=self.pdf_document.current_file_name_dir,
                                               filter=QApplication.translate('CustomStrings', 'PDF files (*.pdf)'))[0]
        if filename:
            self.pdf_document.saveas_doc(filename)
            self.parentWidget().currentWidget().deleteLater()
            self.parentWidget().currentWidget().close()
            self.saveas_signal.emit(filename)

    def doc_zoom_in(self):
        self.current_zoom += 0.25 if self.current_zoom < 3.0 else 3.0
        self.zoom_label.setText(str(int(self.current_zoom * 100)) + '%')
        self.pdfpages_paint()

    def doc_zoom_out(self):
        self.current_zoom -= 0.25 if self.current_zoom > 0.25 else 0.25
        self.zoom_label.setText(str(int(self.current_zoom * 100)) + '%')
        self.pdfpages_paint()

    def page_controls(self, state):
        self.delete_action.setEnabled(state)
        self.rotate_cw_action.setEnabled(state)
        self.rotate_ccw_action.setEnabled(state)
        self.extract_action.setEnabled(state)
        self.insert_action.setEnabled(state)
        self.move_action.setEnabled(state)
        self.pagenumber_action.setEnabled(state)
        self.insert_images_action.setEnabled(state)


    def doc_pages_select(self):
        for index in range(0, self.verticalLayoutPDF.count()):
            self.verticalLayoutPDF.itemAt(index).widget().setchecked(False)

        for page in self.listWidgetPages.selectionModel().selectedIndexes():
            self.verticalLayoutPDF.itemAt(page.row()).widget().setchecked(True)
            self.scrollAreaPDF.ensureWidgetVisible(self.verticalLayoutPDF.itemAt(page.row()).widget())

        if len(self.listWidgetPages.selectionModel().selectedIndexes()) == self.verticalLayoutPDF.count():
            self.page_controls(True)
            self.delete_action.setEnabled(False)
            self.checkBoxAllPages.setChecked(True)
            self.move_action.setEnabled(False)
        elif len(self.listWidgetPages.selectionModel().selectedIndexes()) == 0:
            self.page_controls(False)
            self.checkBoxAllPages.setChecked(False)
        else:
            self.page_controls(True)
            self.checkBoxAllPages.setChecked(False)

    def doc_pages_delete(self):
        position = 0
        for page in self.listWidgetPages.selectionModel().selectedIndexes():
            self.pdf_document.delete_page(page.row() - position)
            position += 1
        self.pdfpages_paint()
        self.save_action.setEnabled(True)

    def doc_page_rotate(self, page, degree):
        self.verticalLayoutPDF.itemAt(page).widget().labelPixmap.clear()
        self.verticalLayoutPDF.itemAt(page).widget().labelPixmap.setPixmap(self.pdf_document.rotate_page(page, degree, self.current_zoom))
        self.save_action.setEnabled(True)

    def doc_pages_rotate_cw(self):
        for page in self.listWidgetPages.selectionModel().selectedIndexes():
            degree = self.pdf_document.pdf_doc.load_page(page.row()).rotation
            degree += 90 if degree <= 270 else 0
            self.doc_page_rotate(page.row(), degree)

    def doc_pages_rotate_ccw(self):
        for page in self.listWidgetPages.selectionModel().selectedIndexes():
            degree = self.pdf_document.pdf_doc.load_page(page.row()).rotation
            degree = degree - 90 if degree > 0 else 270
            self.doc_page_rotate(page.row(), degree)

    def doc_pages_extract(self):
        dirname = os.path.normpath(self.pdf_document.current_file_name_dir + '/' +
                                   self.pdf_document.current_file_name_short + '_' +
                                   QApplication.translate('CustomStrings', 'pages'))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        for page in self.listWidgetPages.selectionModel().selectedIndexes():
            self.pdf_document.extract_pages(dirname, page.row())
        mes = QMessageBox
        if mes.information(self, SOFTWARE_NAME + ' v.' + SOFTWARE_VER, QApplication.translate('CustomStrings',
                           'Selected pages extracted to:') + ' ' + dirname, QMessageBox.Ok) == QMessageBox.Ok:
            pass

    def doc_pages_insert(self):
        filename = QFileDialog.getOpenFileName(self, QApplication.translate('CustomStrings', 'Open PDF file'),
                                               os.path.normpath(os.environ['USERPROFILE'] + '/Documents'),
                                               QApplication.translate('CustomStrings', 'PDF files (*.pdf)'))[0]
        if filename:
            preview_pages = dialogPDFPreview(DIALOG_MODE_PAGE, os.path.normpath(filename))
            preview_pages.setWindowTitle(os.path.normpath(filename))
            if preview_pages.exec_():
                receive_counter = 0
                for page_receive in self.listWidgetPages.selectionModel().selectedIndexes():
                    source_counter = 0
                    for page_source in preview_pages.listWidgetPreview.selectionModel().selectedIndexes():
                        start_index = page_receive.row()
                        if preview_pages.radioButtonAfter.isChecked():
                            start_index += 1
                        self.pdf_document.insert_page(preview_pages.pdf_document.pdf_doc, page_source.row(),
                                                      start_index + source_counter + receive_counter)
                        source_counter += 1
                    receive_counter += len(preview_pages.listWidgetPreview.selectionModel().selectedIndexes())
                self.save_action.setEnabled(True)
                self.pdfpages_paint()

    def doc_images_insert(self):
        filenames = QFileDialog.getOpenFileNames(self, QApplication.translate('CustomStrings', 'Open image files'),
                                                 os.path.normpath(os.environ['USERPROFILE'] + '/Documents'),
                                                 QApplication.translate('CustomStrings',
                                                                        'Image files (*.jpg *.bmp *.png)'))[0]
        if len(filenames) > 0:
            preview_files = dialogPDFPreview(DIALOG_MODE_IMAGES, filenames)
            if preview_files.exec_():
                temppdf = fitz.open()
                for image in preview_files.image_list:
                    img = fitz.open(image[1])
                    rect = img[0].rect
                    pdfbytes = img.convert_to_pdf()
                    img.close()
                    imgPDF = fitz.open('pdf', pdfbytes)
                    page = temppdf.new_page(width=rect.width, height=rect.height)
                    page.show_pdf_page(rect, imgPDF, 0)
                temppdf.save(self.pdf_document.temp_file_name + '_imagetmp')
                start_index = 0 if preview_files.radioButtonBefore.isChecked() else 1
                for page in self.listWidgetPages.selectionModel().selectedIndexes():
                    self.pdf_document.pdf_doc.insert_pdf(temppdf, start_at=page.row() + start_index)
                self.save_action.setEnabled(True)
                self.pdf_document.temp_file_process()
                temppdf.close()
                os.remove(self.pdf_document.temp_file_name + '_imagetmp')
                self.pdfpages_paint()

    def doc_pages_move(self):
        preview_pages = dialogPDFPreview(DIALOG_MODE_MOVE, pdfdoc=self.pdf_document,
                                         excludelist=self.listWidgetPages.selectionModel().selectedIndexes())
        if preview_pages.exec_():
            position = 0
            start_index = 0 if preview_pages.radioButtonBefore.isChecked() else 1
            list_index = preview_pages.move_index - self.listWidgetPages.selectionModel().selectedIndexes()[0].row()
            for page in self.listWidgetPages.selectionModel().selectedIndexes():
                if list_index > 0:
                    temp_index = page.row() - position
                    result_index = list_index + start_index + temp_index
                else:
                    temp_index = page.row()
                    result_index = list_index + start_index + temp_index
                if result_index >= self.pdf_document.page_quantity:
                    result_index = -1
                elif result_index < -1:
                    result_index = 0
                if temp_index < 0:
                    temp_index = 0
                elif temp_index >= self.pdf_document.page_quantity:
                    temp_index = self.pdf_document.page_quantity - 1
                self.pdf_document.pdf_doc.move_page(temp_index, result_index)
                self.pdf_document.temp_file_process()
                #print('Index of page: ' + str(temp_index) + ' Position to move: ' + str(result_index))
                position = position + 1
            self.pdf_document.is_changed = True
            self.save_action.setEnabled(True)
            self.pdfpages_paint()

    def doc_pages_number_insert(self):
        for index in self.listWidgetPages.selectionModel().selectedIndexes():
            self.pdf_document.insert_page_number(index.row(), index.row()+1)
        self.save_action.setEnabled(True)
        self.pdfpages_paint()

    def doc_compress(self):
        if self.pdf_document.temp_file_name[-2:-1] == '_':
            self.pdf_document.temp_file_name = self.pdf_document.temp_file_name[:-2]
        self.pdf_document.compress_doc(self.spinBoxCompression.value())
        self.pdf_document.temp_file_name = self.pdf_document.temp_file_name + '_' + str(self.spinBoxCompression.value())
        self.pdf_document.is_changed = True
        self.pdfpages_paint()

    def show_error_message(self):
        error_message = ''
        if self.pdf_document.error_code == ERROR_PDF_READ:
            error_message = QApplication.translate('CustomStrings', 'PDF file open error') + ': ' + \
                            self.pdf_document.current_file_name
        elif self.pdf_document.error_code == ERROR_TEMPFILE_CREATE:
            error_message = QApplication.translate('CustomStrings', 'Temp file create error') + ': ' + \
                            self.pdf_document.temp_file_name
        elif self.pdf_document.error_code == ERROR_TEMPFILE_REMOVE:
            error_message = QApplication.translate('CustomStrings', 'Temp file remove error') + ': ' + \
                            self.pdf_document.temp_file_name
        else:
            error_message = QApplication.translate('CustomStrings', 'Unknown error')
        mes = QMessageBox
        if mes.critical(self, SOFTWARE_NAME + ' v.' + SOFTWARE_VER, error_message, QMessageBox.Ok) == QMessageBox.Ok:
            return -1


    def close_tab(self):
        if self.pdf_document.is_changed:
            qm = QMessageBox()
            if qm.question(self, QApplication.translate('CustomStrings', 'Warning'),
                           QApplication.translate('CustomStrings', 'You have unsaved changes, proceed?'),
                           QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel) == QMessageBox.Ok:
                self.deleteLater()
                return 0
            else:
                return 1
        else:
            self.deleteLater()
            return 0

    def __del__(self):
        if self.pdf_document.temp_file_name[-2:-1] == '_':
            self.pdf_document.temp_file_name = self.pdf_document.temp_file_name[:-2]
        if self.pdf_document and not self.pdf_document.error_code:
            self.pdf_document.close_file()
