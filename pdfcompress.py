from PyQt5.QtWidgets import QLabel, QDialog, QApplication
from PyQt5.QtCore import Qt
import qtawesome as qta
import os
from shutil import move
from pdfparser import PDFParser
from forms.pdfcompdialog import Ui_pdfcompress


class PDFCompress(QDialog, Ui_pdfcompress):
    def __init__(self, filenames, compresslevel):
        super(PDFCompress, self).__init__()
        self.setupUi(self)
        self.forminit()
        self.setMaximumHeight(500)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowSystemMenuHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.compression_level = compresslevel
        self.pdf_files_list = []
        self.result_list = []
        for filename in filenames:
            self.pdf_files_list.append(os.path.normpath(filename))
        self.pdf_doc_list = []
        self.temp_files_comp = []
        if self.pdf_files_list:
            self.compress_update(self.compression_level)

    def forminit(self):
        self.pushButtonCancel.clicked.connect(self.reject_compressing)
        self.pushButtonAction.clicked.connect(self.accept_compressing)
        self.spinBoxCompression.valueChanged.connect(self.compress_update)
        self.setWindowIcon(qta.icon('mdi.file-pdf', color=COLOR_RED))

    def compress_update(self, compresslevel):
        self.pushButtonAction.setEnabled(False)
        self.compression_level = compresslevel
        opened_files = []
        count = 0
        for i in range(0, len(self.pdf_doc_list)):
            opened_files.append(self.pdf_doc_list[i].current_file_name)
        for i in range(0, self.verticalLayoutFilesList.count()):
            item = self.verticalLayoutFilesList.itemAt(i).widget()
            item.deleteLater()
        for filename in self.pdf_files_list:
            index = -1
            try:
                index = opened_files.index(filename)
            except ValueError:
                pass
            if index < 0:
                pdfdocument = PDFParser(os.path.normpath(filename))
                if pdfdocument.error_code == 0:
                    self.pdf_doc_list.append(pdfdocument)
            else:
                pdfdocument = self.pdf_doc_list[index]

            temp_name = pdfdocument.temp_file_name + '_' + str(self.compression_level)
            if not os.path.exists(temp_name):
                pdfdocument.compress_doc(self.compression_level)
                self.temp_files_comp.append(temp_name)
            count += 1
            self.progressBar.setValue(int(count * 100.0 / len(self.pdf_files_list)))
            comp_level = int((pdfdocument.current_file_size / (os.path.getsize(temp_name) // 1024)) * 100 - 100.0)
            label = QLabel(QApplication.translate('CustomStrings', 'File') + ': ' + pdfdocument.current_file_name_short
                           + '.pdf ' + QApplication.translate('CustomStrings', 'Size') + ': ' +
                           str(pdfdocument.current_file_size) + 'KB ' +
                           QApplication.translate('CustomStrings', 'Compressed size') + ': ' +
                           str(os.path.getsize(temp_name) // 1024) + 'KB ' +
                           QApplication.translate('CustomStrings', 'Compress ratio') + ': ' + str(comp_level) + '%')
            self.verticalLayoutFilesList.addWidget(label)
        self.pushButtonAction.setEnabled(True)

    def reject_compressing(self):
        for file in self.temp_files_comp:
            if os.path.exists(file):
                os.remove(file)
        self.reject()

    def accept_compressing(self):
        if self.checkBoxFileName.isChecked():
            temp_list = [file for file in self.temp_files_comp if file.endswith('_' + str(self.compression_level))]
            for index in range(0, len(temp_list)):
                self.result_list.append(move(temp_list[index], os.path.normpath(self.pdf_doc_list[index].current_file_name_dir + '/' +
                                   os.path.basename(temp_list[index])[:-17] + '_' + QApplication.translate('CustomStrings', 'compressed') +
                                   '_' + str(self.compression_level) + '.pdf')))
        else:
            self.result_list = [file for file in self.temp_files_comp if file.endswith('_' + str(self.compression_level))]
        self.accept()

    def __del__(self):
        for filename in self.temp_files_comp:
            result_list = [file for file in self.temp_files_comp if not file.endswith('_' + str(self.compression_level))]
            for filename in result_list:
                if os.path.exists(filename):
                    os.remove(filename)
        for filename in self.pdf_doc_list:
            if filename:
                filename.close_file()
