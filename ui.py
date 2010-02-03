from PyQt4.QtCore import *
from PyQt4.QtGui import *


DEBUG = True


class TrimageTableView(QTableView):

    def __init__(self, parent=None):
        super(TrimageTableView, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            if DEBUG:
                print("Accepting event: %s" % list(event.mimeData().formats()))
            event.accept()
        else:
            if DEBUG:
                print("Rejecting event: %s" % list(event.mimeData().formats()))
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        files = str(event.mimeData().data("text/uri-list")).strip().split()
        for i, file in enumerate(files):
            files[i] = QUrl(QString(file)).toLocalFile()
        for file in files:
            self.emit(SIGNAL("fileDropEvent"), (file))

class Ui_trimage(object):

    def setupUi(self, trimage):
        trimage.setObjectName("trimage")
        trimage.resize(600, 170)
        trimage.setWindowIcon(QIcon("trimage-icon.png"))

        self.centralwidget = QWidget(trimage)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.widget = QWidget(self.centralwidget)
        self.widget.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")

        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frame = QFrame(self.widget)
        self.frame.setObjectName("frame")

        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(10)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.addfiles = QPushButton(self.frame)
        font = QFont()
        font.setPointSize(9)
        self.addfiles.setFont(font)
        self.addfiles.setCursor(Qt.PointingHandCursor)
        icon = QIcon()
        icon.addPixmap(QPixmap("list-add.png"), QIcon.Normal, QIcon.Off)
        self.addfiles.setIcon(icon)
        self.addfiles.setObjectName("addfiles")
        self.addfiles.setAcceptDrops(True)
        self.horizontalLayout.addWidget(self.addfiles)

        self.label = QLabel(self.frame)
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setFrameShadow(QFrame.Plain)
        self.label.setMargin(1)
        self.label.setIndent(10)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        spacerItem = QSpacerItem(498, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.recompress = QPushButton(self.frame)
        font = QFont()
        font.setPointSize(9)
        self.recompress.setFont(font)
        self.recompress.setCursor(Qt.PointingHandCursor)

        icon1 = QIcon()
        icon1.addPixmap(QPixmap("view-refresh.png"), QIcon.Normal, QIcon.Off)

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
        trimage.setWindowTitle(QApplication.translate("trimage", "Trimage image compressor", None, QApplication.UnicodeUTF8))
        self.addfiles.setToolTip(QApplication.translate("trimage", "Add file to the compression list", None, QApplication.UnicodeUTF8))
        self.addfiles.setText(QApplication.translate("trimage", "&Add and compress", None, QApplication.UnicodeUTF8))
        self.addfiles.setShortcut(QApplication.translate("trimage", "Alt+A", None, QApplication.UnicodeUTF8))
        self.label.setText(QApplication.translate("trimage", "Drag and drop images onto the table", None, QApplication.UnicodeUTF8))
        self.recompress.setToolTip(QApplication.translate("trimage", "Recompress selected images", None, QApplication.UnicodeUTF8))
        self.recompress.setText(QApplication.translate("trimage", "&Recompress", None, QApplication.UnicodeUTF8))
        self.recompress.setShortcut(QApplication.translate("trimage", "Alt+R", None, QApplication.UnicodeUTF8))
        self.processedfiles.setToolTip(QApplication.translate("trimage", "Drag files in here", None, QApplication.UnicodeUTF8))
        self.processedfiles.setWhatsThis(QApplication.translate("trimage", "Drag files in here", None, QApplication.UnicodeUTF8))
