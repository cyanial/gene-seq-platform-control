"""
Camera Window 
  reley on gui/camera
           device/camera

2021/11/08

"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from PyQt5.uic import loadUi

class camera_window(QWidget):

    def __init__(self):
        super().__init__()

        self.ui = loadUi('./gui/camera_show.ui', self)
        self.ui.liveButton.clicked.connect(self.slot_handle)

    def slot_handle(self):
        print('aa')
        



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    camera_window = camera_window()
    camera_window.show()
    sys.exit(app.exec())