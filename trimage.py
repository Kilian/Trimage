import sys
from os import system
from os import listdir
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from hurry.filesize import *
from optparse import OptionParser
from ui import Ui_trimage


DEBUG = True


class StartQT4(QMainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_trimage()
        self.ui.setupUi(self)
        # todo use standardKey Quit.
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        # set recompress to false
        self.ui.recompress.setEnabled(False)
        self.imagelist = []
        self.showapp = True

        # connect signals with slots
        QObject.connect(self.ui.addfiles, SIGNAL("clicked()"),
                        self.file_dialog)
        QObject.connect(self.ui.recompress, SIGNAL("clicked()"),
                        self.recompress_files)
        QObject.connect(self.quit_shortcut, SIGNAL("activated()"),
                        qApp, SLOT('quit()'))

        parser = OptionParser(version="%prog 1.0",
            description="GUI front-end to compress png and jpg images via "
                        "optipng and jpegoptim")

        parser.add_option("-f", "--file",
                          action="store", type="string", dest="filename",
                          help="image to compress")

        parser.add_option("-d", "--directory",
                          action="store", type="string", dest="directory",
                          help="directory of images to compress")

        (options, args) = parser.parse_args()

        if options.filename:
            self.file_from_cmd(options.filename)

        if options.directory:
            self.dir_from_cmd(options.directory)

    def dir_from_cmd(self, directory):
        self.showapp = False
        imagedir = listdir(directory)
        for image in imagedir:
            image = directory + "/" + image
            name = QFileInfo(image).fileName()
            if self.checkname(name):
                self.compress_file(image)

    def file_from_cmd(self, image):
        self.showapp = False
        if self.checkname(image):
            self.compress_file(image)

    def file_drop(self):
        print "booya"

    def checkname(self, filename):
        if filename.endsWith("png") or filename.endsWith("jpg"):
            return True

    def file_dialog(self):
        fd = QFileDialog(self)
        images = fd.getOpenFileNames(self,
                                 "Select one or more image files to compress",
                                 "", # directory
                                 "Image files (*.png *.jpg)")
        for image in images:
            if self.checkname(name):
                self.compress_file(image)

    def enable_recompress(self):
        self.ui.recompress.setEnabled(True)

    def recompress_files(self):
        imagelistcopy = self.imagelist
        self.imagelist = []
        for image in imagelistcopy:
            self.compress_file(image[-1])

    def compress_file(self, filename):
        print filename
        oldfile = QFileInfo(filename)
        name = oldfile.fileName()
        oldfilesize = oldfile.size()
        oldfilesizestr = size(oldfilesize, system=alternative)

        if name.endsWith("jpg"):
            runstr = 'jpegoptim --strip-all -f "' + str(filename) + '"'
            runfile = system(runstr)

        elif name.endsWith("png"):
            #runstr = ('optipng -force -o7 "' + str(filename)
            #+ '"; advpng -z4 "' + str(filename) + '"') ## don't do advpng yet
            runstr = 'optipng -force -o7 "' + str(filename) + '"'
            runfile = system(runstr)

        if runfile == 0:
            newfile = QFile(filename)
            newfilesize = newfile.size()
            newfilesizestr = size(newfilesize, system=alternative)

            ratio = 100 - (float(newfilesize) / float(oldfilesize) * 100)
            ratiostr = "%.1f%%" % ratio

            self.imagelist.append(
                (name, oldfilesizestr, newfilesizestr, ratiostr, filename))
            self.update_table()

        else:
            print "uh. not good" #throw dialogbox error or something?

    def update_table(self):
        tview = self.ui.processedfiles

        # set table model
        tmodel = tri_table_model(self, self.imagelist,
            ['Filename', 'Old Size', 'New Size', 'Compressed'])
        tview.setModel(tmodel)

        # set minimum size of table
        vh = tview.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties
        hh = tview.horizontalHeader()
        hh.setStretchLastSection(True)

        # set all row heights
        nrows = len(self.imagelist)
        for row in range(nrows):
                tview.setRowHeight(row, 25)
        tview.setColumnWidth(0, 300)
        #tview.setDragDropMode(QAbstractItemView.DropOnly)
        #tview.setAcceptDrops(True)
        self.enable_recompress()


class tri_table_model(QAbstractTableModel):

    def __init__(self, parent, imagelist, header, *args):
        """
        mydata is list of tuples
        header is list of strings
        tuple length has to match header length
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.imagelist = imagelist
        self.header = header

    def rowCount(self, parent):
        return len(self.imagelist)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.imagelist[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header[col])
        return QVariant()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartQT4()

    if myapp.showapp:
        myapp.show()
    else:
        quit()
    sys.exit(app.exec_())
