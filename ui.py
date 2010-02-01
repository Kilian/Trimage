# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui'
#
# Created: Mon Feb  1 19:37:17 2010
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_trimage(object):
    def setupUi(self, trimage):
        trimage.setObjectName("trimage")
        trimage.resize(600, 170)

        self.centralwidget = QtGui.QWidget(trimage)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")

        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frame = QtGui.QFrame(self.widget)
        self.frame.setObjectName("frame")

        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(10)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.addfiles = QtGui.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.addfiles.setFont(font)
        self.addfiles.setCursor(QtCore.Qt.PointingHandCursor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("list-add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addfiles.setIcon(icon)
        self.addfiles.setObjectName("addfiles")
        self.horizontalLayout.addWidget(self.addfiles)

        self.label = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setFrameShadow(QtGui.QFrame.Plain)
        self.label.setMargin(1)
        self.label.setIndent(10)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        spacerItem = QtGui.QSpacerItem(498, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.recompress = QtGui.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.recompress.setFont(font)
        self.recompress.setCursor(QtCore.Qt.PointingHandCursor)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("view-refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.recompress.setIcon(icon1)
        self.recompress.setCheckable(False)
        self.recompress.setObjectName("recompress")
        self.horizontalLayout.addWidget(self.recompress)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.processedfiles = QtGui.QTableView(self.frame)
        self.processedfiles.setEnabled(True)
        self.processedfiles.setAcceptDrops(True)
        self.processedfiles.setFrameShape(QtGui.QFrame.NoFrame)
        self.processedfiles.setFrameShadow(QtGui.QFrame.Plain)
        self.processedfiles.setLineWidth(0)
        self.processedfiles.setMidLineWidth(0)
        self.processedfiles.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.processedfiles.setTabKeyNavigation(True)
        self.processedfiles.setDragEnabled(True)
        self.processedfiles.setDragDropMode(QtGui.QAbstractItemView.DropOnly)
        self.processedfiles.setAlternatingRowColors(True)
        self.processedfiles.setTextElideMode(QtCore.Qt.ElideRight)
        self.processedfiles.setShowGrid(True)
        self.processedfiles.setGridStyle(QtCore.Qt.NoPen)
        self.processedfiles.setSortingEnabled(True)
        self.processedfiles.setObjectName("processedfiles")
        self.verticalLayout_2.addWidget(self.processedfiles)
        self.verticalLayout.addWidget(self.frame)
        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)
        trimage.setCentralWidget(self.centralwidget)

        self.retranslateUi(trimage)
        QtCore.QMetaObject.connectSlotsByName(trimage)

    def retranslateUi(self, trimage):
        trimage.setWindowTitle(QtGui.QApplication.translate("trimage", "Trimage image compressor", None, QtGui.QApplication.UnicodeUTF8))
        self.addfiles.setToolTip(QtGui.QApplication.translate("trimage", "Add file to the compression list", None, QtGui.QApplication.UnicodeUTF8))
        self.addfiles.setText(QtGui.QApplication.translate("trimage", "&Add and compress", None, QtGui.QApplication.UnicodeUTF8))
        self.addfiles.setShortcut(QtGui.QApplication.translate("trimage", "Alt+A", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("trimage", "Drag and drop images onto the table", None, QtGui.QApplication.UnicodeUTF8))
        self.recompress.setToolTip(QtGui.QApplication.translate("trimage", "Recompress selected images", None, QtGui.QApplication.UnicodeUTF8))
        self.recompress.setText(QtGui.QApplication.translate("trimage", "&Recompress", None, QtGui.QApplication.UnicodeUTF8))
        self.recompress.setShortcut(QtGui.QApplication.translate("trimage", "Alt+R", None, QtGui.QApplication.UnicodeUTF8))
        self.processedfiles.setToolTip(QtGui.QApplication.translate("trimage", "Drag files in here", None, QtGui.QApplication.UnicodeUTF8))
        self.processedfiles.setWhatsThis(QtGui.QApplication.translate("trimage", "Drag files in here", None, QtGui.QApplication.UnicodeUTF8))

