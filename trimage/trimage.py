#!/usr/bin/env python3

import time
import sys
from os import listdir, path, remove, access, W_OK
from shutil import copy

from optparse import OptionParser
from multiprocessing import cpu_count
from queue import Queue

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ThreadPool import ThreadPool
from ui import Ui_trimage
from tools import *


VERSION = "1.0.6"


class StartQt(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_trimage()
        self.ui.setupUi(self)

        self.showapp = True
        self.verbose = True
        self.imagelist = []

        QCoreApplication.setOrganizationName("Kilian Valkhof")
        QCoreApplication.setOrganizationDomain("trimage.org")
        QCoreApplication.setApplicationName("Trimage")
        self.settings = QSettings()
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))

        # check if dependencies are installed
        if not check_dependencies():
            quit()

        # add quit shortcut
        if hasattr(QKeySequence, "Quit"):
            self.quit_shortcut = QShortcut(QKeySequence(QKeySequence.Quit),
                self)
        else:
            self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)

        # disable recompress
        self.ui.recompress.setEnabled(False)

        # make a worker thread
        self.thread = Worker()

        # connect signals with slots
        self.ui.addfiles.clicked.connect(self.file_dialog)
        self.ui.recompress.clicked.connect(self.recompress_files)
        self.quit_shortcut.activated.connect(self.close)
        self.ui.processedfiles.drop_event_signal.connect(self.file_drop)
        self.thread.finished.connect(self.update_table)
        self.thread.update_ui_signal.connect(self.update_table)

        self.compressing_icon = QIcon(QPixmap(self.ui.get_image("pixmaps/compressing.gif")))

        # activate command line options
        self.commandline_options()

        if QSystemTrayIcon.isSystemTrayAvailable() and not self.cli:
            self.systemtray = Systray(self)

    def commandline_options(self):
        """Set up the command line options."""
        self.cli = False
        parser = OptionParser(version="%prog " + VERSION,
            description="GUI front-end to compress png and jpg images via "
                "advpng, jpegoptim, optipng and pngcrush")

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
            self.thread.finished.connect(quit)
            self.cli = True

        # send to correct function
        if options.filename:
            self.file_from_cmd(options.filename)
        if options.directory:
            self.dir_from_cmd(options.directory)

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
        if (self.settings.value("fdstate")):
            fd.restoreState(self.settings.value("fdstate"))
        directory = self.settings.value("directory", QVariant(""))
        fd.setDirectory(directory)

        images, _ = fd.getOpenFileNames(self,
            "Select one or more image files to compress",
            directory,
            # this is a fix for file dialog differentiating between cases
            "Image files (*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG)")

        self.settings.setValue("fdstate", QVariant(fd.saveState()))
        if images:
            self.settings.setValue("directory", QVariant(path.dirname(images[0])))
            self.delegator([fullpath for fullpath in images])

    def recompress_files(self):
        """Send each file in the current file list to compress_file again."""
        self.delegator([row.image.fullpath for row in self.imagelist])

    """
    Compress functions
    """

    def delegator(self, images):
        """
        Receive all images, check them and send them to the worker thread.
        """
        delegatorlist = []
        for fullpath in images:
            try: # recompress images already in the list
                image = next(i.image for i in self.imagelist
                    if i.image.fullpath == fullpath)
                if image.compressed:
                    image.reset()
                    image.recompression = True
                    delegatorlist.append(image)
            except StopIteration:
                if not path.isdir(fullpath):
                    self.add_image(fullpath, delegatorlist)
                else:
                    self.walk(fullpath, delegatorlist)

        self.update_table()
        self.thread.compress_file(delegatorlist, self.showapp, self.verbose,
            self.imagelist)

    def walk(self, dir, delegatorlist):
        """
        Walks a directory, and executes a callback on each file.
        """
        dir = path.abspath(dir)
        for file in [file for file in listdir(dir) if not file in [".","..",".svn",".git",".hg",".bzr",".cvs"]]:
            nfile = path.join(dir, file)

            if path.isdir(nfile):
                self.walk(nfile, delegatorlist)
            else:
                self.add_image(nfile, delegatorlist)

    def add_image(self, fullpath, delegatorlist):
        """
        Adds an image file to the delegator list and update the tray and the title of the window.
        """
        image = Image(fullpath)
        if image.valid:
            delegatorlist.append(image)
            self.imagelist.append(ImageRow(image, self.compressing_icon))
            if QSystemTrayIcon.isSystemTrayAvailable() and not self.cli:
                self.systemtray.trayIcon.setToolTip("Trimage image compressor (" + str(len(self.imagelist)) + " files)")
                self.setWindowTitle("Trimage image compressor (" + str(len(self.imagelist)) + " files)")
        else:
            print("[error] {} not a supported image file and/or not writable".format(image.fullpath), file=sys.stderr)

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

    def enable_recompress(self):
        """Enable the recompress button."""
        self.ui.recompress.setEnabled(True)
        if QSystemTrayIcon.isSystemTrayAvailable() and not self.cli:
            self.systemtray.recompress.setEnabled(True)

    def hide_main_window(self):
        if self.isVisible():
            self.hide()
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.systemtray.hideMain.setText("&Show window")
        else:
            self.show()
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.systemtray.hideMain.setText("&Hide window")

    def closeEvent(self, event):
      self.settings.setValue("geometry", QVariant(self.saveGeometry()))
      event.accept()


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
        """Build the information visible in the table image row."""
        self.image = image
        d = {
            'filename_w_ext': lambda i: self.statusStr() % i.filename_w_ext,
            'oldfilesizestr': lambda i: human_readable_size(i.oldfilesize)
                if i.compressed else "",
            'newfilesizestr': lambda i: human_readable_size(i.newfilesize)
                if i.compressed else "",
            'ratiostr': lambda i:
                "%.1f%%" % (100 - (float(i.newfilesize) / i.oldfilesize * 100))
                if i.compressed else "",
            'icon': lambda i: i.icon if i.compressed else waitingIcon,
            'fullpath': lambda i: i.fullpath, #only used by cli
        }
        names = ['filename_w_ext', 'oldfilesizestr', 'newfilesizestr',
                      'ratiostr', 'icon']
        for i, n in enumerate(names):
            d[i] = d[n]

        self.d = d

    def statusStr(self):
        """Set the status message."""
        if self.image.failed:
            return "ERROR: %s"
        if self.image.compressing:
            message = "Compressing %s..."
            return message
        if not self.image.compressed and self.image.recompression:
            return "Queued for recompression..."
        if not self.image.compressed:
            return "Queued..."
        return "%s"

    def __getitem__(self, key):
        return self.d[key](self.image)


class Image:
    def __init__(self, fullpath):
        """Gather image information."""
        self.valid = False
        self.reset()
        self.fullpath = fullpath
        self.filename_w_ext = path.basename(self.fullpath)
        self.filename, self.filetype = path.splitext(self.filename_w_ext)
        if path.isfile(self.fullpath) and access(self.fullpath, W_OK):
            self.filetype = self.filetype[1:].lower()
            if self.filetype == "jpg":
                self.filetype = "jpeg"
            if self.filetype in ["jpeg", "png"]:
                oldfile = QFileInfo(self.fullpath)
                self.oldfilesize = oldfile.size()
                self.icon = QIcon(self.fullpath)
                self.valid = True

    def reset(self):
        self.failed = False
        self.compressed = False
        self.compressing = False
        self.recompression = False

    def compress(self):
        """Compress the image and return it to the thread."""
        if not self.valid:
            raise "Tried to compress invalid image (unsupported format or not \
            file)"
        self.reset()
        self.compressing = True
        exe = ".exe" if (sys.platform == "win32") else ""
        runString = {
            "jpeg": "jpegoptim" + exe + " -f --strip-all '%(file)s'",
            "png": "optipng" + exe + " -force -o7 '%(file)s'&&advpng" + exe + " -z4 '%(file)s' && pngcrush -rem gAMA -rem alla -rem cHRM -rem iCCP -rem sRGB -rem time '%(file)s' '%(file)s.bak' && mv '%(file)s.bak' '%(file)s'"
        }
        # create a backup file
        backupfullpath = '/tmp/' + self.filename_w_ext
        copy(self.fullpath, backupfullpath)
        try:
            retcode = call(runString[self.filetype] % {"file": self.fullpath},
                shell=True, stdout=PIPE)
        except:
            retcode = -1
        if retcode == 0:
            self.newfilesize = QFile(self.fullpath).size()
            self.compressed = True

            # checks the new file and copy the backup
            if self.newfilesize >= self.oldfilesize:
                copy(backupfullpath, self.fullpath)
                self.newfilesize = self.oldfilesize

            # removes the backup file
            remove(backupfullpath)
        else:
            self.failed = True
        self.compressing = False
        self.retcode = retcode
        return self


class Worker(QThread):
    update_ui_signal = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.toDisplay = Queue()
        self.threadpool = ThreadPool(max_workers=cpu_count())

    def __del__(self):
        self.threadpool.shutdown()

    def compress_file(self, images, showapp, verbose, imagelist):
        """Start the worker thread."""
        for image in images:
            #FIXME:http://code.google.com/p/pythonthreadpool/issues/detail?id=5
            time.sleep(0.05)
            self.threadpool.add_job(image.compress, None,
                                    return_callback=self.toDisplay.put)
        self.showapp = showapp
        self.verbose = verbose
        self.imagelist = imagelist
        self.start()

    def run(self):
        """Compress the given file, get data from it and call update_table."""
        tp = self.threadpool
        while self.showapp or not (tp._ThreadPool__active_worker_count == 0 and
                                   tp._ThreadPool__jobs.empty()):
            image = self.toDisplay.get()

            self.update_ui_signal.emit()

            if not self.showapp and self.verbose: # we work via the commandline
                if image.retcode == 0:
                    ir = ImageRow(image)
                    print("File: " + ir['fullpath'] + ", Old Size: "
                        + ir['oldfilesizestr'] + ", New Size: "
                        + ir['newfilesizestr'] + ", Ratio: " + ir['ratiostr'])
                else:
                    print("[error] {} could not be compressed".format(image.fullpath), file=sys.stderr)


class Systray(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent
        self.createActions()
        self.createTrayIcon()
        self.trayIcon.show()

    def createActions(self):
        self.quitAction = QAction(self.tr("&Quit"), self)
        self.quitAction.triggered.connect(self.parent.close)

        self.addFiles = QAction(self.tr("&Add and compress"), self)
        icon = QIcon()
        icon.addPixmap(QPixmap(self.parent.ui.get_image(("pixmaps/list-add.png"))),
            QIcon.Normal, QIcon.Off)
        self.addFiles.setIcon(icon)
        self.addFiles.triggered.connect(self.parent.file_dialog)

        self.recompress = QAction(self.tr("&Recompress"), self)
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(self.parent.ui.get_image(("pixmaps/view-refresh.png"))),
            QIcon.Normal, QIcon.Off)
        self.recompress.setIcon(icon2)
        self.recompress.setDisabled(True)

        self.addFiles.triggered.connect(self.parent.recompress_files)

        self.hideMain = QAction(self.tr("&Hide window"), self)
        self.hideMain.triggered.connect(self.parent.hide_main_window)

    def createTrayIcon(self):
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.addFiles)
        self.trayIconMenu.addAction(self.recompress)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.hideMain)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        if QSystemTrayIcon.isSystemTrayAvailable():
            self.trayIcon = QSystemTrayIcon(self)
            self.trayIcon.setContextMenu(self.trayIconMenu)
            self.trayIcon.setToolTip("Trimage image compressor")
            self.trayIcon.setIcon(QIcon(self.parent.ui.get_image("pixmaps/trimage-icon.png")))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = StartQt()

    if myapp.showapp:
        myapp.show()
    sys.exit(app.exec_())
