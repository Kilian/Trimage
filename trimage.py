import sys
from PyQt4 import QtCore, QtGui
from ui import Ui_trimage
from os.path import isfile

class StartQT4(QtGui.QMainWindow):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.ui = Ui_trimage()
    self.ui.setupUi(self)

    # connect signals with slots
    QtCore.QObject.connect(self.ui.addfiles,QtCore.SIGNAL("clicked()"), self.file_dialog)
    QtCore.QObject.connect(self.ui.recompress,QtCore.SIGNAL("clicked()"), self.recompress_files)

    # set recompress to false
    self.ui.recompress.setEnabled(False)

  def file_dialog(self):
    fd = QtGui.QFileDialog(self)
    images = fd.getOpenFileNames(self,
                         "Select one or more image files to compress",
                         "", # directory
                         "Image files (*.png *.gif *.jpg)")

    for image in images:
      filename = image
      oldfilesize = QtCore.QFileInfo(image).size()
      # send image to processing

  def enable_recompress(self):
    self.ui.recompress.setEnabled(True)

  def recompress_files(self):
    # get list of currently processed files
    # reprocess them
    # update columnview
    self.setWindowTitle("check too!")

  def compress_file(self, filename):
    # check file extention
    # get file size
    # run correct command line tool and get reply
    # get new file size
    # add to columnview
    self.setWindowTitle("check too!")

  def add_to_columnview(self):
    # update column view with file info
    self.setWindowTitle("check too!")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())

