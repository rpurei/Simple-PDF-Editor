# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms\pdfpage.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_pagePDF(object):
    def setupUi(self, pagePDF):
        pagePDF.setObjectName("pagePDF")
        pagePDF.resize(195, 114)
        pagePDF.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayoutPage = QtWidgets.QVBoxLayout(pagePDF)
        self.verticalLayoutPage.setObjectName("verticalLayoutPage")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayoutPage.addItem(spacerItem)
        self.labelPageIndex = QtWidgets.QLabel(pagePDF)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelPageIndex.sizePolicy().hasHeightForWidth())
        self.labelPageIndex.setSizePolicy(sizePolicy)
        self.labelPageIndex.setText("")
        self.labelPageIndex.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPageIndex.setObjectName("labelPageIndex")
        self.verticalLayoutPage.addWidget(self.labelPageIndex)
        self.horizontalLayoutPage = QtWidgets.QHBoxLayout()
        self.horizontalLayoutPage.setObjectName("horizontalLayoutPage")
        self.verticalLayoutPage.addLayout(self.horizontalLayoutPage)
        self.labelPixmap = QtWidgets.QLabel(pagePDF)
        self.labelPixmap.setText("")
        self.labelPixmap.setScaledContents(False)
        self.labelPixmap.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPixmap.setObjectName("labelPixmap")
        self.verticalLayoutPage.addWidget(self.labelPixmap)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayoutPage.addItem(spacerItem1)

        self.retranslateUi(pagePDF)
        QtCore.QMetaObject.connectSlotsByName(pagePDF)

    def retranslateUi(self, pagePDF):
        _translate = QtCore.QCoreApplication.translate
        pagePDF.setWindowTitle(_translate("pagePDF", "Form"))