import sys
from PyQt4 import QtCore, QtGui
from ui import Ui_trimage

class StartQT4(QtGui.QMainWindow):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.ui = Ui_trimage()
    self.ui.setupUi(self)
    self.quit_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Q"),  self); # todo use standardKey Quit.

    # connect signals with slots
    QtCore.QObject.connect(self.ui.addfiles, QtCore.SIGNAL("clicked()"), self.file_dialog)
    QtCore.QObject.connect(self.ui.recompress, QtCore.SIGNAL("clicked()"), self.recompress_files)
    QtCore.QObject.connect(self.quit_shortcut, QtCore.SIGNAL("activated()"), QtGui.qApp, QtCore.SLOT('quit()'))

    # set recompress to false
    self.ui.recompress.setEnabled(False)


  def file_dialog(self):
    fd = QtGui.QFileDialog(self)
    images = fd.getOpenFileNames(self,
                                 "Select one or more image files to compress",
                                 "", # directory
                                 "Image files (*.png *.gif *.jpg)")
    for image in images:
      self.compress_file(image)


  def enable_recompress(self):
    self.ui.recompress.setEnabled(True)


  def recompress_files(self):
    # get list of currently processed files
    # reprocess them
    # update columnview
    self.setWindowTitle("check too!")


  def compress_file(self, filename):
    oldfile = QtCore.QFileInfo(filename);
    name = oldfile.fileName()
    oldfilesize = oldfile.size()

    if name.endsWith("jpg"):
      self.jpg = True
      # run jpegoptim
    else:
      self.jpg = False
      #run optipng

    newfile = oldfile
    newfilesize = newfile.size()
    ratio = 100 - (newfilesize / oldfilesize * 100)
    ratio_str = "%.1f%%" % ratio

    # get new file size
    # add to columnview name, newsize, ratio_str,

  def add_to_tableview(self, filename, filesize, ratio):
    # update table view with file info
    self.setWindowTitle("check too!")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())

