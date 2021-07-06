# Simple PDF Editor

This application is designed for PDF files simple manipulation.
At this moment application supports locales:
- English
- Russian

## Features:

- rotate selected pages;

- delete selected pages;

- export selected pages to separate JPG files;

- import selected pages from another PDF file;

- import selected images as pages of PDF document;

- rearrange selected pages in PDF file;

- insert numeration on selected pages of PDF file;

- multiple PDF files compression;

- multiple PDF files merging;

- multiple BMP, PNG and JPG files merging in one PDF file.

## Tech

Simple PDF Editor uses a number of projects to work properly:

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - great library for modifying PDF documents
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI library
- [QtAwesome](https://github.com/spyder-ide/qtawesome) - awesome icons
- [Qt-Material](https://pypi.org/project/qt-material/) - material design look for Qt
- [Ghostscript](https://www.ghostscript.com/) - for compressing PDF files

## Installation

Install the dependencies and run main.py.

```sh
python -m pip install -r requirements.txt
python main.py
```

## Development

Want to contribute? You are welcome, make forks, locales,

## License

GPLv3


