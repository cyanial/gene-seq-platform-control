"""
Camera Window 
  reley on gui/camera
           device/camera

2021/11/08

"""

import qimage2ndarray

import pyqtgraph as pg

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

        # pg.setConfigOptions(antialias=True)
        self.state.sig_camera_status.connect(self.updateStatus)
        self.liveButton.clicked.connect(self.live)
        self.SnapButton.clicked.connect(self.snap)
        self.liveTimer = QtCore.QTimer()
        self.liveTimer.timeout.connect(self.live_image)

    @QtCore.pyqtSlot()
    def live_image(self):
        state = self.state.getCamera().getStatus()
        self.statusLabel.setText(state)
        if state == 'IDLE':
            self.image = self.state.getCamera().acquireData()
            self.showImage()
            self.state.getCamera().startAcquisition()

        
    @QtCore.pyqtSlot()
    def live(self):
        if self.living:
            self.living = False
            self.liveButton.setText('live')
            self.state.getCamera().abortAcquisition()
            self.liveTimer.stop()
        else:
            self.living = True
            self.liveButton.setText('stop')
            self.state.getCamera().startAcquisition()
            self.liveTimer.start(self.state.exposureTime() * 1000)

    @QtCore.pyqtSlot()
    def snap(self):
        self.state.getCamera().startAcquisition()
        self.snapping = True
        self.liveButton.setEnabled(False)

    @QtCore.pyqtSlot()
    def showImage(self):
        self.image_view.setImage(self.image, autoLevels=True, autoRange=True, autoHistogramRange=True)
    
    @QtCore.pyqtSlot(str)
    def updateStatus(self, state):
        if self.living:
            return
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
