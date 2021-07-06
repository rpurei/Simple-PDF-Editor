#TODO: темная тема, редактирование текста, драг-дроп порядка страниц

import sys
import locale
import fitz
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QWidget, QLabel, QTextBrowser
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QMimeData
import qtawesome as qta
from pdfparser import *
from qt_material import apply_stylesheet, list_themes
from forms.mainwindow import Ui_MainWindow
from pdfpreview import dialogPDFPreview
from pdfdoc import PDFDoc
from pdfparser import PDFParser
from pdfcompress import PDFCompress
from const import *


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.translator = QtCore.QTranslator()

        get_locale = locale.getdefaultlocale()[0]
        if get_locale.startswith('us_') or get_locale.startswith('en_'):
            get_locale = 'us_EN'
        self.current_locale = get_locale if get_locale else DEFAULT_LOCALE
        self.locales_dir = os.path.dirname(os.path.realpath(__file__)) + r'/locales/'
        if not os.path.exists(self.locales_dir):
            mes = QMessageBox
            if mes.critical(self, SOFTWARE_NAME + ' v.' + SOFTWARE_VER,
                            QApplication.translate('CustomStrings', 'Locales dir not found, only english enabled'),
                            QMessageBox.Ok, QMessageBox.Ok) == QMessageBox.Ok:
                pass
        self.flags_dir = os.path.dirname(os.path.realpath(__file__)) + r'/images/icons/flags/'
        self.supported_locales = self.getsupportedlocales()
        self.setupUi(self)
        self.showMaximized()
        self.forminit()
        self.setWindowIcon(qta.icon('mdi.file-pdf', color=COLOR_RED))
        self.show()

    change_locale_signal = pyqtSignal()

    def closeEvent(self, event):
        if self.appclose():
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        super(MainWindow, self).dragEnterEvent(event)
        if event.mimeData().urls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        super(MainWindow, self).dropEvent(event)
        for filenameurl in event.mimeData().urls():
            filename = filenameurl.toLocalFile()
            self.add_tab(filename)

    def getsupportedlocales(self):
        supported_locales = [DEFAULT_LOCALE]
        if os.path.exists(self.locales_dir):
            for file in os.listdir(self.locales_dir):
                if file.endswith(LOCALE_EXT):
                    supported_locales.append(file.split('.')[0])
        return supported_locales

    def formlocalessetup(self):
        for loc in self.supported_locales:
            action = QtWidgets.QAction(QtGui.QIcon(os.path.normpath(self.flags_dir + loc.split('_')[0] + FLAGS_EXT)),
                                       loc.upper(), self)
            action.setCheckable(True)
            if loc == self.current_locale:
                action.setChecked(True)
                font = QtGui.QFont()
                font.setBold(True)
                action.setFont(font)
                self.setwindowlocale(loc)
            action.triggered.connect(self.localechange)
            self.menuLanguage.addAction(action)

    def formthemessetup(self):
        font = QtGui.QFont()
        font.setBold(True)
        for theme in list_themes():
            if 'dark' not in theme:
                action = QtWidgets.QAction(theme[:-4].upper(), self)
                action.setCheckable(True)
                action.triggered.connect(self.themechange)
                self.menuTheme.addAction(action)
        self.menuTheme.actions()[1].trigger()

    def themechange(self):
        font = QtGui.QFont()
        for act in self.menuTheme.actions():
            act.setChecked(False)
            font.setBold(False)
            act.setFont(font)
        self.sender().setChecked(True)
        font.setBold(True)
        self.sender().setFont(font)
        apply_stylesheet(self, theme=self.sender().text() + '.xml')

    def setwindowlocale(self, locale):
        locale_file = os.path.normpath(self.locales_dir + locale + LOCALE_EXT)
        help_file = os.path.normpath(self.locales_dir + locale + HELP_EXT)
        self.help_file = help_file if os.path.isfile(help_file) else None
        if os.path.isfile(locale_file):
            self.current_locale = locale
            if self.translator.load(locale_file):
                QtWidgets.qApp.instance().installTranslator(self.translator)
            else:
                QtWidgets.qApp.instance().removeTranslator(self.translator)
        else:
            QtWidgets.qApp.instance().removeTranslator(self.translator)
        self.retranslateUi(self)
        self.setWindowTitle(SOFTWARE_NAME + ' v.' + SOFTWARE_VER)
        self.change_locale_signal.emit()

    def forminit(self):
        self.setAcceptDrops(True)
        self.formlocalessetup()
        self.formthemessetup()
        self.fileToolBar = QtWidgets.QToolBar()
        self.fileToolBar.addAction(self.actionOpen)
        self.fileToolBar.addAction(self.actionMerge)
        self.fileToolBar.addAction(self.actionCompress)
        self.fileToolBar.addAction(self.actionMergeImages)
        self.fileToolBar.addAction(self.actionExit)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.fileToolBar)
        self.actionExit.triggered.connect(self.appclose)
        self.actionExit.setIcon(qta.icon('mdi.exit-to-app', color=COLOR_RED))
        self.actionOpen.triggered.connect(self.openfiles)
        self.actionMerge.triggered.connect(self.mergefiles)
        self.actionCompress.triggered.connect(self.compressfiles)
        self.actionMergeImages.triggered.connect(self.mergeimages)
        self.actionOpen.setIcon(qta.icon('mdi.folder-open-outline', color = COLOR_GREEN))
        self.actionMerge.setIcon(qta.icon('mdi.select-group', color = COLOR_BLUE))
        self.actionCompress.setIcon(qta.icon('mdi.buffer', color=COLOR_BLUE))
        self.actionMergeImages.setIcon(qta.icon('mdi.file-multiple-outline', color=COLOR_BLUE))
        self.menuLanguage.setIcon(qta.icon('mdi.flag-variant-outline'))
        self.menuTheme.setIcon(qta.icon('mdi.format-paint'))
        self.tabPDFWidget.setTabIcon(0, qta.icon('mdi.home-outline'))
        self.actionAbout.triggered.connect(self.aboutshow)
        self.actionHelp.triggered.connect(self.helpshow)
        self.label_status = QLabel()
        self.statusbar.addWidget(self.label_status)
        self.label_status.setText(QApplication.translate('CustomStrings', 'Open files for modifying, merging '
                                                                          'or compressing'))

    def localechange(self):
        font = QtGui.QFont()
        for act in self.menuLanguage.actions():
            act.setChecked(False)
            font.setBold(False)
            act.setFont(font)
        self.sender().setChecked(True)
        font.setBold(True)
        self.sender().setFont(font)
        self.setwindowlocale(self.sender().text())

    def openfiles(self):
        filenames = QFileDialog.getOpenFileNames(self, QApplication.translate('CustomStrings', 'Open PDF files'),
                                                 os.path.normpath(os.environ['USERPROFILE'] + '/Documents'),
                                                 QApplication.translate('CustomStrings', 'PDF files (*.pdf)'))[0]
        if len(filenames) > 0:
            for file in filenames:
                self.add_tab(file)
            self.label_status.setText(QApplication.translate('CustomStrings', 'All files are opened'))

    @QtCore.pyqtSlot(str)
    def saveas_open(self, filename):
        self.add_tab(filename)

    def mergefiles(self):
        filenames = QFileDialog.getOpenFileNames(self, QApplication.translate('CustomStrings', 'Open PDF files'),
                                                 os.path.normpath(os.environ['USERPROFILE'] + '/Documents'),
                                                 QApplication.translate('CustomStrings', 'PDF files (*.pdf)'))[0]
        if len(filenames) > 0:
            preview_files = dialogPDFPreview(DIALOG_MODE_FILE, filenames)
            if preview_files.exec():
                filename = QFileDialog.getSaveFileName(self, QApplication.translate('CustomStrings', 'Save PDF file'),
                                                       directory=preview_files.pdf_documents[0].current_file_name_dir,
                                                       filter=QApplication.translate('CustomStrings',
                                                                                     'PDF files (*.pdf)'))[0]
                firstpdf = PDFParser(os.path.normpath(preview_files.pdf_documents[0].current_file_name))
                if firstpdf.error_code == 0:
                    for index in range(1, len(preview_files.pdf_documents)):
                        temppdf = PDFParser(os.path.normpath(preview_files.pdf_documents[index].current_file_name))
                        if temppdf.error_code == 0:
                            firstpdf.pdf_doc.insert_pdf(temppdf.pdf_doc)
                        else:
                            self.show_error_message(temppdf)
                    firstpdf.saveas_doc(filename)
                    self.add_tab(filename)
                else:
                    self.show_error_message(firstpdf)
                self.label_status.setText(QApplication.translate('CustomStrings', 'All files are merged to file:')
                                          + ' ' + filename)

    def compressfiles(self):
        filenames = QFileDialog.getOpenFileNames(self, QApplication.translate('CustomStrings', 'Open PDF files'),
                                                 os.path.normpath(os.environ['USERPROFILE'] + '/Documents'),
                                                 QApplication.translate('CustomStrings', 'PDF files (*.pdf)'))[0]
        self.label_status.setText(QApplication.translate('CustomStrings', 'Processing'))
        if len(filenames) > 0:
            compress_tab = PDFCompress(filenames, DEFAULT_COMPRESS_LEVEL)
            if compress_tab.exec_():
                for file in compress_tab.result_list:
                    self.add_tab(file)
                    if os.path.exists(file) and not compress_tab.checkBoxFileName.isChecked():
                        os.remove(file)
            self.label_status.setText(QApplication.translate('CustomStrings', 'All files compressed'))

    def mergeimages(self):
        filenames = QFileDialog.getOpenFileNames(self, QApplication.translate('CustomStrings', 'Open image files'),
                                                 os.path.normpath(os.environ['USERPROFILE'] + '/Documents'),
                                                 QApplication.translate('CustomStrings',
                                                                        'Image files (*.jpg *.bmp *.png)'))[0]
        if len(filenames) > 0:
            preview_files = dialogPDFPreview(DIALOG_MODE_IMAGE, filenames)
            if preview_files.exec_():
                filename = QFileDialog.getSaveFileName(self, QApplication.translate('CustomStrings', 'Save PDF file'),
                                                       os.path.normpath(os.environ['USERPROFILE'] + '/Documents'),
                                                       filter=QApplication.translate('CustomStrings',
                                                                                     'PDF files (*.pdf)'))[0]
                temppdf = fitz.open()
                for image in preview_files.image_list:
                    img = fitz.open(image[1])
                    rect = img[0].rect
                    pdfbytes = img.convert_to_pdf()
                    img.close()
                    imgPDF = fitz.open("pdf", pdfbytes)
                    page = temppdf.new_page(width=rect.width, height=rect.height)
                    page.show_pdf_page(rect, imgPDF, 0)
                temppdf.save(os.path.normpath(filename))
                self.add_tab(filename)
                self.label_status.setText(QApplication.translate('CustomStrings', 'All files are merged to file:')
                                          + ' ' + filename)

    def add_tab(self, file):
        file = os.path.normpath(file)
        pdf_tab = PDFDoc(file)
        if not pdf_tab.pdf_document.error_code:
            pdf_tab.saveas_signal.connect(self.saveas_open)
            self.change_locale_signal.connect(pdf_tab.retranslate)
            self.tabPDFWidget.addTab(pdf_tab, qta.icon('mdi.file-pdf-outline'),
                                    pdf_tab.pdf_document.current_file_name_short + '.pdf')
            self.tabPDFWidget.setCurrentIndex(self.tabPDFWidget.count() - 1)

    def aboutshow(self):
        self.label = QLabel(SOFTWARE_NAME + ' v.' + SOFTWARE_VER + '\n' +
                            QApplication.translate('CustomStrings', 'License: GPLv2') + '\n' +
                            QApplication.translate('CustomStrings', 'Developed: Purey Roman rpurey@gmail.com') + '\n' +
                            QApplication.translate('CustomStrings', 'Used libs:') + 'PyQt5, PyMuPDF, QtAwesome, Qt-Material')

        self.label.setMinimumHeight(300)
        self.label.setMinimumWidth(400)
        self.label.setMaximumHeight(300)
        self.label.setMaximumWidth(400)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label.setWindowTitle(QApplication.translate('CustomStrings', 'About program'))
        self.label.setWindowModality(Qt.ApplicationModal)
        self.label.show()

    def helpshow(self):
        self.browser = QTextBrowser()
        self.browser.setWindowTitle(QApplication.translate('MainWindow', 'Help'))
        self.browser.setMinimumHeight(600)
        self.browser.setMinimumWidth(800)
        self.browser.setMaximumHeight(600)
        self.browser.setMaximumWidth(800)
        self.browser.setText(self.help_file)
        if self.help_file:
            self.browser.setSource(QtCore.QUrl.fromLocalFile(self.help_file))
        self.browser.setWindowModality(Qt.ApplicationModal)
        self.browser.show()

    def show_error_message(self, pdfdoc):
        error_message = ''
        if pdfdoc.error_code == ERROR_PDF_READ:
            error_message = QApplication.translate('CustomStrings', 'PDF file open error') + \
                                                    ': ' + pdfdoc.current_file_name
        elif pdfdoc.error_code == ERROR_TEMPFILE_CREATE:
            error_message = QApplication.translate('CustomStrings', 'Temp file create error') + \
                                                    ': ' + pdfdoc.temp_file_name
        elif pdfdoc.error_code == ERROR_TEMPFILE_REMOVE:
            error_message = QApplication.translate('CustomStrings', 'Temp file remove error') + \
                                                    ': ' + pdfdoc.temp_file_name
        else:
            error_message = QApplication.translate('CustomStrings', 'Unknown error') + \
                                                    ': ' + pdfdoc.temp_file_name
        mes = QMessageBox
        if mes.critical(self, SOFTWARE_NAME + ' v.' + SOFTWARE_VER, error_message, QMessageBox.Ok) == QMessageBox.Ok:
            return -1

    def appclose(self):
        if self.tabPDFWidget.count() > 0:
            for i in range(0, self.tabPDFWidget.count()):
                item = self.tabPDFWidget.widget(i)
                if item.pdf_document.is_changed:
                    self.tabPDFWidget.setCurrentIndex(i)
                if item.close_tab():
                    return False
        QApplication.exit(0)
        return True


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    ret = app.exec_()
    sys.exit(ret)
