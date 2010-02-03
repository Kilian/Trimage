import sys
from os import system
from os import listdir
from os import path
from subprocess import *
from optparse import OptionParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from hurry.filesize import *

from ui import Ui_trimage


DEBUG = True


class StartQT4(QMainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_trimage()
        self.ui.setupUi(self)
        #TODO use standardKey Quit.
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)

        # disable recompress
        self.ui.recompress.setEnabled(False)

        # init imagelist
        self.imagelist = []

        # show application on load (or not if there are command line options)
        self.showapp = True

        # activate command line options
        self.commandline_options()

        # connect signals with slots
        QObject.connect(self.ui.addfiles, SIGNAL("clicked()"),
            self.file_dialog)
        QObject.connect(self.ui.recompress, SIGNAL("clicked()"),
            self.recompress_files)
        QObject.connect(self.quit_shortcut, SIGNAL("activated()"),
            qApp, SLOT('quit()'))
        QObject.connect(self.ui.processedfiles, SIGNAL("fileDropEvent"),
            self.file_drop)

    def commandline_options(self):
        """Set up the command line options."""
        parser = OptionParser(version="%prog 1.0",
            description="GUI front-end to compress png and jpg images via "
                "optipng, advpng and jpegoptim")
        parser.add_option("-f", "--file", action="store", type="string",
            dest="filename", help="compresses image and exit")
        parser.add_option("-d", "--directory", action="store", type="string",
            dest="directory", help="compresses images in directory and exit", )

        options, args = parser.parse_args()

        # do something with the file or directory
        if options.filename:
            self.file_from_cmd(options.filename)
        if options.directory:
            self.dir_from_cmd(options.directory)

    def dir_from_cmd(self, directory):
        """Read the files in the directory and send all files to
        compress_file."""
        self.showapp = False
        imagedir = listdir(directory)
        for image in imagedir:
            image = path.join(directory, image)
            name = QFileInfo(image).fileName()
            if self.checkname(name):
                self.compress_file(image)

    def file_from_cmd(self, image):
        """Get the file and send it to compress_file"""
        self.showapp = False
        if self.checkname(image):
            self.compress_file(image)

    def file_drop(self, image):
        """Get a file from the drag and drop handler and send it to
        compress_file."""
        if self.checkname(image):
            self.compress_file(image)


    def checkname(self, name):
        """Check if the file is a jpg or png."""
        if path.splitext(str(name))[1].lower() in [".jpg", ".jpeg", ".png"]:
            return True

    def file_dialog(self):
        """Open a file dialog and send the selected images to compress_file."""
        fd = QFileDialog(self)
        images = fd.getOpenFileNames(self,
            "Select one or more image files to compress",
            "", # directory
            # this is a fix for file dialog differenciating between cases
            "Image files (*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG)")
        for image in images:
            if self.checkname(image):
                self.compress_file(image)

    def enable_recompress(self):
        """Enable the recompress button."""
        self.ui.recompress.setEnabled(True)

    def recompress_files(self):
        """Send each file in the current file list to compress_file again."""
        imagelistcopy = self.imagelist
        self.imagelist = []
        for image in imagelistcopy:
            self.compress_file(image[-1])

    def compress_file(self, filename):
        """Compress the given file, get data from it and call update_table."""

        #gather old file data
        oldfile = QFileInfo(filename)
        name = oldfile.fileName()
        oldfilesize = oldfile.size()
        oldfilesizestr = size(oldfilesize, system=alternative)

        #decide with tool to use
        if path.splitext(str(filename))[1].lower() in [".jpg", ".jpeg"]:
            runstr = 'jpegoptim -f --strip-all "' + str(filename) + '"'
            try:
                retcode = call(runstr, shell=True, stdout=PIPE)
                runfile = retcode
            except OSError, e:
                runfile = e
        elif path.splitext(str(filename))[1].lower() in [".png"]:
            runstr = ('optipng -force -o7 "' + str(filename)
                      + '"; advpng -z4 "' + str(filename) + '"')
            try:
                retcode = call(runstr, shell=True, stdout=PIPE)
                runfile = retcode
            except OSError, e:
                runfile = e

        if runfile == 0:
            #gather new file data
            newfile = QFile(filename)
            provider = QFileIconProvider()
            newfileicon = provider.icon(QFileInfo(filename))
            newfilesize = newfile.size()
            newfilesizestr = size(newfilesize, system=alternative)

            #calculate ratio and make a nice string
            ratio = 100 - (float(newfilesize) / float(oldfilesize) * 100)
            ratiostr = "%.1f%%" % ratio

            # append current image to list
            self.imagelist.append(
                (newfileicon, name, oldfilesizestr, newfilesizestr, ratiostr,
                filename))
            self.update_table()

            if self.showapp != True:
                # we work via the commandline
                print("File:" + filename + ", Old Size:" + oldfilesizestr +
                      ", New Size:" + newfilesizestr + ", Ratio:" + ratiostr)

        else:
            # TODO nice error recovery
            print("uh. not good")

    def update_table(self):
        """Update the table view with the latest file data."""
        tview = self.ui.processedfiles

        # set table model
        tmodel = TriTableModel(self, self.imagelist,
            ["", "Filename", "Old Size", "New Size", "Compressed"])
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

        # set the second column to be longest
        tview.setColumnWidth(0, 30)
        tview.setColumnWidth(1, 280)

        # enable recompress button
        self.enable_recompress()


class TriTableModel(QAbstractTableModel):

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
        """Count the number of rows."""
        return len(self.imagelist)

    def columnCount(self, parent):
        """Count the number of columns."""
        return len(self.header)

    def data(self, index, role):
        """Get data."""
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.imagelist[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        """Get header data."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header[col])
        return QVariant()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartQT4()

    if myapp.showapp:
        # no command line options called
        myapp.show()
    else:
        quit()
    sys.exit(app.exec_())
