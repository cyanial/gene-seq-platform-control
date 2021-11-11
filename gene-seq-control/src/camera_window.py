"""
Camera Window 
  reley on gui/camera
           device/camera

2021/11/08

"""

import qimage2ndarray

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QGraphicsScene

from PyQt5.uic import loadUi

from .main_state import state_singleton

class camera_window(QDialog):

    def __init__(self, state):
        super().__init__()

        loadUi('gui/camera_show.ui', self)
        self.state = state_singleton()
        self.snapping = False
        self.living = False
        self.image = None

        self.state.sig_camera_status.connect(self.updateStatus)
        self.liveButton.clicked.connect(self.live)
        self.SnapButton.clicked.connect(self.snap)
        self.histoButton.clicked.connect(self.histogram)

    @QtCore.pyqtSlot()
    def histogram(self):
        if self.image:
            pass
        
    @QtCore.pyqtSlot()
    def live(self):
        if self.living:
            self.living = False
            self.liveButton.setText('live')
            # self.state.getCamera().abortAcquisition()
        else:
            self.living = True
            self.liveButton.setText('stop')
            # self.state.getCamera().startAcquisition()

    @QtCore.pyqtSlot()
    def snap(self):
        self.state.getCamera().startAcquisition()
        self.snapping = True
        self.liveButton.setEnabled(False)

    @QtCore.pyqtSlot()
    def showImage(self):
        if self.autoScaleChecked.isChecked():
            # print('do auto scale')
            # arr = self.image
            # new_arr = ((arr - arr.min()) * (1/(arr.max() - arr.min()) * 255)).astype('uint8')
            # self.image = new_arr
            pass
        scene = QGraphicsScene(self)
        scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(self.image)))
        self.graphicsView.setScene(scene)
        # tifffile.imsave('test.tif', self.image)
    
    @QtCore.pyqtSlot(str)
    def updateStatus(self, state):
        self.statusLabel.setText(state)
        if state == 'IDLE':
            if self.snapping:
                self.snapping = False
                self.liveButton.setEnabled(True)
                self.image = self.state.getCamera().acquireData()
                self.showImage()
                # print(self.image)





if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    camera_window = camera_window()
    camera_window.show()
    sys.exit(app.exec())
