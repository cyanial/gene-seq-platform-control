"""
Camera Window 
  reley on gui/camera
           device/camera

2021/11/08

"""

from PyQt5.QtWidgets import QDialog

from PyQt5.uic import loadUi

class camera_window(QDialog):

    def __init__(self):
        super().__init__()

        loadUi('gui/camera_show.ui', self)
        self.liveButton.clicked.connect(self.slot_handle)

    def slot_handle(self):
        print('aa')
        



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    camera_window = camera_window()
    camera_window.show()
    sys.exit(app.exec())
