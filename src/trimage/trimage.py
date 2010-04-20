#!/usr/bin/python
import time
import sys
import errno
from os import listdir
from os import path
from subprocess import call, PIPE
from optparse import OptionParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from filesize import *
from imghdr import what as determinetype

from Queue import Queue
from ThreadPool import ThreadPool
from multiprocessing import cpu_count

from ui import Ui_trimage

VERSION = "1.0.0b3"


class StartQT4(QMainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_trimage()
        self.ui.setupUi(self)

        self.showapp = True
        self.verbose = True
        self.imagelist = []

        # check if apps are installed
        if self.checkapps():
            quit()

        #add quit shortcut
        if hasattr(QKeySequence, "Quit"):
            self.quit_shortcut = QShortcut(QKeySequence(QKeySequence.Quit),
                self)
        else:
            self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)

        # disable recompress
        self.ui.recompress.setEnabled(False)
        #self.ui.recompress.hide()

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

        parser.set_defaults(verbose=True)
        parser.add_option("-v", "--verbose", action="store_true",
            dest="verbose", help="Verbose mode (default)")
        parser.add_option("-q", "--quiet", action="store_false",
            dest="verbose", help="Quiet mode")

        parser.add_option("-f", "--file", action="store", type="string",
            dest="filename", help="compresses image and exit")
        parser.add_option("-d", "--directory", action="store", type="string",
            dest="directory", help="compresses images in directory and exit")

        options, args = parser.parse_args()

        # make sure we quit after processing finished if using cli
        if options.filename or options.directory:
            QObject.connect(self.thread, SIGNAL("finished()"), quit)

        # send to correct function
        if options.filename:
            self.file_from_cmd(options.filename.decode("utf-8"))
        if options.directory:
            self.dir_from_cmd(options.directory.decode("utf-8"))

        self.verbose = options.verbose

    """
    Input functions
    """

    def dir_from_cmd(self, directory):
        """
        Read the files in the directory and send all files to compress_file.
        """
        self.showapp = False
        dirpath = path.abspath(directory)
        imagedir = listdir(directory)
        filelist = [path.join(dirpath, image) for image in imagedir]
        self.delegator(filelist)

    def file_from_cmd(self, image):
        """Get the file and send it to compress_file"""
        self.showapp = False
        filelist = [path.abspath(image)]
        self.delegator(filelist)

    def file_drop(self, images):
        """
        Get a file from the drag and drop handler and send it to compress_file.
        """
        self.delegator(images)

    def file_dialog(self):
        """Open a file dialog and send the selected images to compress_file."""
        fd = QFileDialog(self)
        images = fd.getOpenFileNames(self,
            "Select one or more image files to compress",
            "", # directory
            # this is a fix for file dialog differentiating between cases
            "Image files (*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG)")

        self.delegator([unicode(fullpath) for fullpath in images])

    def recompress_files(self):
        """Send each file in the current file list to compress_file again."""
        self.delegator([row.image.fullpath for row in self.imagelist])

    """
    Compress functions
    """

    def delegator(self, images):
        """
        Recieve all images, check them and send them to the worker thread.
        """
        delegatorlist = []
        for fullpath in images:
            try: # do not add already existing images again, recompress them instead
                image=(i.image for i in self.imagelist
                    if i.image.fullpath == fullpath).next()
                if image.compressed:
                  image.reset()
                  image.recompression=True
                  delegatorlist.append(image)
            except StopIteration:
                image=Image(fullpath)
                if image.valid:
                    delegatorlist.append(image)
                    self.imagelist.append(ImageRow(image,QIcon(QPixmap(self.ui.get_image("pixmaps/compressing.gif")))))
                else:
                    print >>sys.stderr, u"[error] %s not a supported image file" % image.fullpath

        self.update_table()
        self.thread.compress_file(delegatorlist, self.showapp, self.verbose,
            self.imagelist)


    """
    UI Functions
    """

    def update_table(self):
        """Update the table view with the latest file data."""
        tview = self.ui.processedfiles
        # set table model
        tmodel = TriTableModel(self, self.imagelist,
            ["Filename", "Old Size", "New Size", "Compressed"])
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
        tview.setColumnWidth(0, 300)

        # enable recompress button
        self.enable_recompress()

    """
    Helper functions
    """

    def enable_recompress(self):
        """Enable the recompress button."""
        self.ui.recompress.setEnabled(True)

    def checkapps(self):
        """Check if the required command line apps exist."""
        exe=".exe" if (sys.platform=="win32") else ""
        status = False
        retcode = self.safe_call("jpegoptim"+exe+" --version")
        if retcode != 0:
            status = True
            sys.stderr.write("[error] please install jpegoptim")

        retcode = self.safe_call("optipng"+exe+" -v")
        if retcode != 0:
            status = True
            sys.stderr.write("[error] please install optipng")

        retcode = self.safe_call("advpng"+exe+" --version")
        if retcode != 0:
            status = True
            sys.stderr.write("[error] please install advancecomp")
        return status

    def safe_call(self, command):
        """ cross-platform command-line check """
        while True:
            try:
                return call(command, shell=True, stdout=PIPE)
            except OSError, e:
                if e.errno == errno.EINTR:
                    continue
                else:
                    raise

class TriTableModel(QAbstractTableModel):

    def __init__(self, parent, imagelist, header, *args):
        """
        @param parent Qt parent object.
        @param imagelist A list of tuples.
        @param header A list of strings.
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
        """Fill the table with data."""
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole:
            data = self.imagelist[index.row()][index.column()]
            return QVariant(data)
        elif index.column() == 0 and role == Qt.DecorationRole:
            # decorate column 0 with an icon of the image itself
            f_icon = self.imagelist[index.row()][4]
            return QVariant(f_icon)
        else:
            return QVariant()

    def headerData(self, col, orientation, role):
        """Fill the table headers."""
        if orientation == Qt.Horizontal and (role == Qt.DisplayRole or
        role == Qt.DecorationRole):
            return QVariant(self.header[col])
        return QVariant()
        
class ImageRow:
    def __init__(self, image, waitingIcon=None):
        self.image=image
        d={
            'shortname':      lambda i: self.statusStr() % i.shortname,
            'oldfilesizestr': lambda i: size(i.oldfilesize, system=alternative) if i.compressed else "",
            'newfilesizestr': lambda i: size(i.newfilesize, system=alternative) if i.compressed else "",
            'ratiostr':       lambda i:
                "%.1f%%" % (100 - (float(i.newfilesize) / i.oldfilesize * 100)) if i.compressed else "",
            'icon':           lambda i: i.icon if i.compressed else waitingIcon,

            'fullpath':       lambda i: i.fullpath, #only used by cli
        }
        for i,n in enumerate(['shortname','oldfilesizestr','newfilesizestr','ratiostr','icon']):
            d[i]=d[n]
        
        self.d = d

    def statusStr(self):
        if self.image.failed:
            return "ERROR: %s"
        if self.image.compressing:
            return "In Progress..."
        if not self.image.compressed and self.image.recompression:
            return "Queued for recompression..."
        if not self.image.compressed:
            return "Queued..."
        return "%s"

    def __getitem__(self, key):
        return self.d[key](self.image)

class Image:
    def __init__(self, fullpath):
        self.valid = False
        self.reset()
        self.fullpath = fullpath
        if path.isfile(self.fullpath):            
            self.filetype = determinetype(self.fullpath)
            if self.filetype in ["jpeg", "png"]:
                oldfile = QFileInfo(self.fullpath)
                self.shortname = oldfile.fileName()
                self.oldfilesize = oldfile.size()
                self.icon = QIcon(self.fullpath)
                self.valid = True

    def _determinetype(self):
        filetype=determinetype(self.fullpath)
        if filetype in ["jpeg", "png"]:
            self.filetype=filetype
        else:
            self.filetype=None
        return self.filetype

    def reset(self):
        self.failed = False
        self.compressed = False
        self.compressing = False
        self.recompression= False

    def compress(self):
        if not self.valid:
            raise "Tried to compress invalid image (unsupported format or not file)"
        self.reset()
        self.compressing=True
        exe=".exe" if (sys.platform=="win32") else ""
        runString = {
            "jpeg": u"jpegoptim"+exe+" -f --strip-all '%(file)s'",
            "png" : u"optipng"+exe+" -force -o7 '%(file)s'&&advpng"+exe+" -z4 '%(file)s'"}
        try:
            retcode = call(runString[self.filetype] % {"file": self.fullpath},
                shell = True, stdout=PIPE)
        except:
          retcode = -1
        if retcode == 0:
            self.newfilesize = QFile(self.fullpath).size()
            self.compressed=True
        else:
            self.failed=True
        self.compressing=False
        self.retcode=retcode
        return self


class Worker(QThread):

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.toDisplay=Queue()
        self.threadpool = ThreadPool(max_workers=cpu_count())

    def __del__(self):
        self.threadpool.shutdown()

    def compress_file(self, images, showapp, verbose, imagelist):
        """Start the worker thread."""
        for image in images:
            time.sleep(0.05) #FIXME: Workaround http://code.google.com/p/pythonthreadpool/issues/detail?id=5
            self.threadpool.add_job(image.compress, None, return_callback=self.toDisplay.put)
        self.showapp = showapp
        self.verbose = verbose
        self.imagelist = imagelist
        self.start()

    def run(self):
        """Compress the given file, get data from it and call update_table."""
        tp = self.threadpool
        while self.showapp or not (tp._ThreadPool__active_worker_count==0 and tp._ThreadPool__jobs.empty()):
            image = self.toDisplay.get()
            self.emit(SIGNAL("updateUi"))

            if not self.showapp and self.verbose: # we work via the commandline
                if image.retcode==0:                                    
                    ir=ImageRow(image)
                    print("File: " + ir['fullpath'] + ", Old Size: "
                        + ir['oldfilesizestr'] + ", New Size: " + ir['newfilesizestr']
                        + ", Ratio: " + ir['ratiostr'])
                else:
                    print >>sys.stderr, u"[error] %s could not be compressed" % image.fullpath


class TrimageTableView(QTableView):
    """Init the table drop event."""
    def __init__(self, parent=None):
        super(TrimageTableView, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        files = str(event.mimeData().data("text/uri-list")).strip().split()
        for i, file in enumerate(files):
            files[i] = QUrl(QString(file)).toLocalFile()
        files=[i.toUtf8().decode("utf-8") for i in files]
        self.emit(SIGNAL("fileDropEvent"), (files))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartQT4()

    if myapp.showapp:
        myapp.show()
    sys.exit(app.exec_())
