from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from os import path

class TrimageTableView(QTableView):
    """Init the table drop event."""
    def __init__(self, parent=None):
        super(TrimageTableView, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        event.accept()
        filelist = []
        for url in event.mimeData().urls():
            filelist.append(url.toLocalFile())

        self.emit(SIGNAL("fileDropEvent"), (filelist))


class Ui_trimage(object):
    def get_image(self, image):
        """ Get the correct link to the images used in the UI """
        imagelink = path.join(path.dirname(path.dirname(path.realpath(__file__))), "trimage/" + image)
        return imagelink

    def setupUi(self, trimage):
        """ Setup the entire UI """
        trimage.setObjectName("trimage")
        trimage.resize(600, 170)

        trimageIcon = QIcon(self.get_image("pixmaps/trimage-icon.png"))
        trimage.setWindowIcon(trimageIcon)

        self.centralwidget = QWidget(trimage)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.widget = QWidget(self.centralwidget)
        self.widget.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")

        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frame = QFrame(self.widget)
        self.frame.setObjectName("frame")

        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.addfiles = QPushButton(self.frame)
        font = QFont()
        font.setPointSize(9)
        self.addfiles.setFont(font)
        self.addfiles.setCursor(Qt.PointingHandCursor)
        icon = QIcon()
        icon.addPixmap(QPixmap(self.get_image("pixmaps/list-add.png")), QIcon.Normal, QIcon.Off)
        self.addfiles.setIcon(icon)
        self.addfiles.setObjectName("addfiles")
        self.addfiles.setAcceptDrops(True)
        self.horizontalLayout.addWidget(self.addfiles)

        self.label = QLabel(self.frame)
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setFrameShadow(QFrame.Plain)
        self.label.setContentsMargins(1, 1, 1, 1)
        self.label.setIndent(10)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        spacerItem = QSpacerItem(498, 20, QSizePolicy.Expanding,
                                 QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.recompress = QPushButton(self.frame)
        font = QFont()
        font.setPointSize(9)
        self.recompress.setFont(font)
        self.recompress.setCursor(Qt.PointingHandCursor)

        icon1 = QIcon()
        icon1.addPixmap(QPixmap(self.get_image("pixmaps/view-refresh.png")), QIcon.Normal, QIcon.Off)

        self.recompress.setIcon(icon1)
        self.recompress.setCheckable(False)
        self.recompress.setObjectName("recompress")
        self.horizontalLayout.addWidget(self.recompress)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.processedfiles = TrimageTableView(self.frame)
        self.processedfiles.setEnabled(True)
        self.processedfiles.setFrameShape(QFrame.NoFrame)
        self.processedfiles.setFrameShadow(QFrame.Plain)
        self.processedfiles.setLineWidth(0)
        self.processedfiles.setMidLineWidth(0)
        self.processedfiles.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.processedfiles.setTabKeyNavigation(True)
        self.processedfiles.setAlternatingRowColors(True)
        self.processedfiles.setTextElideMode(Qt.ElideRight)
        self.processedfiles.setShowGrid(True)
        self.processedfiles.setGridStyle(Qt.NoPen)
        self.processedfiles.setSortingEnabled(False)
        self.processedfiles.setObjectName("processedfiles")
        self.processedfiles.resizeColumnsToContents()
        self.processedfiles.setSelectionMode(QAbstractItemView.NoSelection)
        self.verticalLayout_2.addWidget(self.processedfiles)
        self.verticalLayout.addWidget(self.frame)
        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)
        trimage.setCentralWidget(self.centralwidget)

        self.retranslateUi(trimage)
        QMetaObject.connectSlotsByName(trimage)

    def retranslateUi(self, trimage):
        """ Fill in the texts for all UI elements """
        trimage.setWindowTitle(QApplication.translate("trimage",
            "Trimage image compressor", None))
        self.addfiles.setToolTip(QApplication.translate("trimage",
            "Add file to the compression list", None))
        self.addfiles.setText(QApplication.translate("trimage",
            "&Add and compress", None))
        self.addfiles.setShortcut(QApplication.translate("trimage",
            "Alt+A", None))
        self.label.setText(QApplication.translate("trimage",
            "Drag and drop images onto the table", None))
        self.recompress.setToolTip(QApplication.translate("trimage",
            "Recompress all images", None))
        self.recompress.setText(QApplication.translate("trimage",
            "&Recompress", None))
        self.recompress.setShortcut(QApplication.translate("trimage",
            "Alt+R", None))
        self.processedfiles.setToolTip(QApplication.translate("trimage",
            "Drag files in here", None))
        self.processedfiles.setWhatsThis(QApplication.translate("trimage",
            "Drag files in here", None))
