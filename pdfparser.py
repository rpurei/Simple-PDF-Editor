import fitz
import os
import tempfile
import string
import random
from shutil import copy, move
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from const import *
import subprocess


class PDFParser():
    def __init__(self, pdffilename):
        self.error_code = 0
        self.current_file_name = pdffilename
        self.temp_file_name = os.path.join(tempfile.gettempdir(), os.path.basename(self.current_file_name) + '_tmp_' +
                                           ''.join(random.choice(string.ascii_uppercase +
                                                                 string.digits) for _ in range(6)))
        self.current_file_name_dir = os.path.dirname(self.current_file_name)
        self.current_file_name_short = os.path.splitext(os.path.basename(self.current_file_name))[0]
        try:
            copy(pdffilename, self.temp_file_name)
        except:
            self.error_code = ERROR_TEMPFILE_CREATE
        if self.error_code != ERROR_TEMPFILE_CREATE:
            try:
                self.pdf_doc = fitz.Document(self.temp_file_name)
            except:
                self.error_code = ERROR_PDF_READ
        if not self.error_code:
            self.page_quantity = len(self.pdf_doc)
            self.current_file_size = os.path.getsize(self.current_file_name) // 1024
            self.is_changed = False
            self.pdf_doc_pages = []

    def get_page(self, pagenumber, zoom):
        temp_doc = fitz.Document(self.temp_file_name)
        page = temp_doc.load_page(pagenumber)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(alpha=False)
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        pixmap = QPixmap.fromImage(QImage(pix.samples, pix.width, pix.height, pix.stride, fmt))
        pixmap_scaled = pixmap.scaled(int(pixmap.width() * zoom), int(pixmap.height() * zoom), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        temp_doc.close()
        return pixmap_scaled

    def render_pages(self, zoom):
        self.pdf_doc_pages.clear()
        for page in range(0, self.page_quantity):
            self.pdf_doc_pages.append(self.get_page(page, zoom))

    def rotate_page(self, page, degree, zoom):
        page_rotate = self.pdf_doc.load_page(page)
        page_rotate.set_rotation(degree)
        self.temp_file_process()
        return self.get_page(page, zoom)

    def delete_page(self, page):
        self.pdf_doc.delete_page(page)
        self.temp_file_process()

    def extract_pages(self, dirname, index):
        self.pdf_doc.load_page(index).get_pixmap(alpha=False).pillowWrite(os.path.normpath(dirname + '/' + self.current_file_name_short +
                                                                          '_' + str(index + 1) + '.jpg'), optimize=True, dpi=(300, 300))

    def insert_page(self, pages_source, source_page_index, start_at):
        self.pdf_doc.insert_pdf(pages_source, from_page=source_page_index, to_page=source_page_index, start_at=start_at)
        self.temp_file_process()

    def insert_page_number(self, page, number):
        insert_page = self.pdf_doc.load_page(page)
        insert_point = insert_page.bound()
        where = fitz.Point(int(insert_point.x1*0.95), int(insert_point.y1*0.95))
        insert_page.insert_text(where, str(number))
        self.temp_file_process()

    def compress_doc(self, compress_power):
        if not os.path.exists(self.temp_file_name + '_' + str(compress_power)):
            subprocess.call(['gswin32c', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                            '-dPDFSETTINGS={}'.format(quality[compress_power]),
                            '-dNOPAUSE', '-dQUIET', '-dBATCH', '-sOutputFile={}'.format(self.temp_file_name + '_' + str(compress_power)),
                            self.current_file_name], shell=False)

    def temp_file_process(self):
        self.pdf_doc.save(self.temp_file_name + '_', garbage=1)
        self.pdf_doc.close()
        if os.path.exists(move(self.temp_file_name + '_', self.temp_file_name)):
            self.pdf_doc = fitz.Document(self.temp_file_name)
            self.page_quantity = len(self.pdf_doc)
            self.is_changed = True
        else:
            self.error_code = ERROR_TEMPFILE_CREATE

    def save_doc(self):
        self.pdf_doc.save(self.temp_file_name + '_', garbage=1)
        self.is_changed = False
        if os.path.exists(copy(self.temp_file_name + '_', self.current_file_name)):
            if os.path.exists(move(self.temp_file_name + '_', self.temp_file_name)):
                pass
            else:
                self.error_code = ERROR_TEMPFILE_CREATE
        else:
            self.error_code = ERROR_TEMPFILE_CREATE

    def saveas_doc(self, filename):
        self.pdf_doc.save(filename, garbage=1)

    def close_file(self):
        if self.error_code != ERROR_TEMPFILE_CREATE and self.pdf_doc:
            self.pdf_doc.close()
        for index in range(0, 5):
            if os.path.isfile(self.temp_file_name + '_' + str(index)):
                os.remove(self.temp_file_name + '_' + str(index))
        if os.path.isfile(self.temp_file_name):
            os.remove(self.temp_file_name)
        return self.error_code
