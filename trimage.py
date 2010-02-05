import sys
from os import system
from os import listdir
import os.path
from subprocess import *
from optparse import OptionParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from hurry.filesize import *

from ui import Ui_trimage

VERSION = "1.0"
DEBUG = True

#init imagelist
imagelist = []

# show application on load (or not if there are command line options)
showapp = True

class StartQT4(QMainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_trimage()
        self.ui.setupUi(self)
        if hasattr(QKeySequence, 'Quit'):
            self.quit_shortcut = QShortcut(QKeySequence(QKeySequence.Quit), self)
        else:
            self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)

        # disable recompress
        self.ui.recompress.setEnabled(False)

        # make a worker thread
        self.thread = Worker()

        # connect signals with slots
        QObject.connect(self.ui.addfiles, SIGNAL("clicked()"),
            self.file_dialog)
        QObject.connect(self.ui.recompress, SIGNAL("clicked()"),
            self.recompress_files)
        QObject.connect(self.quit_shortcut, SIGNAL("activated()"),
            qApp, SLOT('quit()'))
        QObject.connect(self.ui.processedfiles, SIGNAL("fileDropEvent"),
            self.file_drop)
        QObject.connect(self.thread, SIGNAL("finished()"), self.update_table)
        QObject.connect(self.thread, SIGNAL("terminated()"), self.update_table)
        QObject.connect(self.thread, SIGNAL("updateUi"), self.update_table)

        # activate command line options
        self.commandline_options()

    def commandline_options(self):
        """Set up the command line options."""
        parser = OptionParser(version="%prog " + VERSION,
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
    """
    Input functions
    """
    def dir_from_cmd(self, directory):
        """Read the files in the directory and send all files to
        compress_file."""
        global showapp
        showapp = False
        dirpath = os.path.abspath(os.path.dirname(directory))
        imagedir = listdir(directory)
        filelist = QStringList()
        for image in imagedir:
            image = QString(os.path.join(dirpath, image))
            filelist.append(image)
        self.delegator(filelist)

    def file_from_cmd(self, image):
        """Get the file and send it to compress_file"""
        global showapp
        showapp = False
        image = os.path.abspath(image)
        filecmdlist = QStringList()
        filecmdlist.append(image)
        self.delegator(filecmdlist)

    def file_drop(self, images):
        """Get a file from the drag and drop handler and send it to
        compress_file."""
        print images[0]
        self.delegator(images)

    def file_dialog(self):
        """Open a file dialog and send the selected images to compress_file."""
        fd = QFileDialog(self)
        images = fd.getOpenFileNames(self,
            "Select one or more image files to compress",
            "", # directory
            # this is a fix for file dialog differenciating between cases
            "Image files (*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG)")
        self.delegator(images)

    def recompress_files(self):
        """Send each file in the current file list to compress_file again."""
        newimagelist = []

        global imagelist
        for image in imagelist:
            newimagelist.append(image[4])
        imagelist = []
        self.delegator(newimagelist)
    """
    Compress functions
    """
    def delegator(self, images):
        delegatorlist = []
        for image in images:
            if self.checkname(image):
                delegatorlist.append((image, QIcon(image)))
                #TODO figure out how to animate
                imagelist.append(("Compressing...", "", "", "", image, QIcon(QPixmap("compressing.gif"))))
        self.thread.compress_file(delegatorlist)

    """
    UI Functions
    """
    def update_table(self):
        """Update the table view with the latest file data."""
        tview = self.ui.processedfiles
        # set table model
        tmodel = TriTableModel(self, imagelist,
            ["Filename", "Old Size", "New Size", "Compressed"])
        tview.setModel(tmodel)

        # set minimum size of table
        vh = tview.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties
        hh = tview.horizontalHeader()
        hh.setStretchLastSection(True)

        # set all row heights
        nrows = len(imagelist)
        for row in range(nrows):
            tview.setRowHeight(row, 25)

        # set the second column to be longest
        tview.setColumnWidth(0, 300)

        # enable recompress button
        self.enable_recompress()

    """
    Helper functions
    """
    def checkname(self, name):
        """Check if the file is a jpg or png."""
        if os.path.splitext(str(name))[1].lower() in [".jpg", ".jpeg", ".png"]:
            return True

    def enable_recompress(self):
        """Enable the recompress button."""
        self.ui.recompress.setEnabled(True)

class TriTableModel(QAbstractTableModel):

    def __init__(self, parent, imagelist, header, *args):
        """
        imagelist is list of tuples
        header is list of strings
        tuple length has to match header length
        """
        QAbstractTableModel.__init__(self, parent, *args)
        imagelist = imagelist
        self.header = header

    def rowCount(self, parent):
        """Count the number of rows."""
        return len(imagelist)

    def columnCount(self, parent):
        """Count the number of columns."""
        return len(self.header)

    def data(self, index, role):
        """Get data."""
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole:
            data = imagelist[index.row()][index.column()]
            return QVariant(data)
        elif index.column()==0 and role == Qt.DecorationRole:
            # decorate column 0 with an icon of the image itself
            f_icon = imagelist[index.row()][5]
            return QVariant(f_icon)
        else:
            return QVariant()

    def headerData(self, col, orientation, role):
        """Get header data."""
        if orientation == Qt.Horizontal and (role == Qt.DisplayRole or
        role == Qt.DecorationRole):
            return QVariant(self.header[col])
        return QVariant()


class Worker(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def compress_file(self, images):
        self.images = images
        self.start()

    def run(self):
        """Compress the given file, get data from it and call update_table."""
        for image in self.images:
            #gather old file data
            filename = str(image[0])

            icon = image[1]
            oldfile = QFileInfo(filename)
            name = oldfile.fileName()
            oldfilesize = oldfile.size()
            oldfilesizestr = size(oldfilesize, system=alternative)
            print type(filename)
            # get extention
            baseName, extention = os.path.splitext(filename)
            
            #decide with tool to use
            if extention in ['.jpg', '.jpeg']:
                runString = 'jpegoptim -f --strip-all "%(file)s"' 
            elif extention in ['.png']:
                runString = 'optipng -force -o7 "%(file)s"; advpng -z4 "%(file)s"'
            else:
                # This probably should never happen...
                raise Exception('File %s does not have the appropriate extention' % filename)
                          
            try:
                retcode = call(runString % {'file' : filename}, shell = True, stdout = PIPE)
                runfile = retcode
            except OSError, e:
                runfile = e
               
            if runfile != 0:
                # TODO nice error recovery
                raise Exception('Some error occurred!')
        
            
            #gather new file data
            newfile = QFile(filename)
            newfilesize = newfile.size()
            newfilesizestr = size(newfilesize, system=alternative)

            #calculate ratio and make a nice string
            ratio = 100 - (float(newfilesize) / float(oldfilesize) * 100)
            ratiostr = "%.1f%%" % ratio

            # append current image to list
            for i, image in enumerate(imagelist):
                if image[4] == filename:
                    imagelist.remove(image)
                    imagelist.insert(i, (name, oldfilesizestr, newfilesizestr, ratiostr,
                              filename, icon))
            self.emit(SIGNAL("updateUi"))

            global showapp
            if not showapp:
                # we work via the commandline
                print("File:" + filename + ", Old Size:" + oldfilesizestr +
                      ", New Size:" + newfilesizestr + ", Ratio:" + ratiostr)
           

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartQT4()

    if showapp:
        # no command line options called
        myapp.show()
    else:
        quit()
    sys.exit(app.exec_())
