"""
Camera Window 
  reley on gui/camera
           device/camera

2021/11/08

"""

import pyqtgraph as pg

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog

from PyQt5.uic import loadUi

from .main_state import state_singleton
from .camera import camera

import logging
logger = logging.getLogger(__name__)

class camera_window(QDialog):

    sig_snap = QtCore.pyqtSignal()
    sig_acquiredata = QtCore.pyqtSignal()
    sig_abort = QtCore.pyqtSignal()
    sig_live_on = QtCore.pyqtSignal()
    sig_live_off = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        logger.debug('create camera window')
        loadUi('gui/camera_show.ui', self)
        self.camera_worker = camera()
        self.state = state_singleton()
        self.snapping = False
        self.living = False

        pg.setConfigOptions(antialias=True)
        self.camera_worker.sig_state_camera_status.connect(self.updateStatus)
        self.sig_snap.connect(self.camera_worker.startAcquisition)
        self.sig_acquiredata.connect(self.camera_worker.acquireData)
        self.camera_worker.sig_image_data_ready.connect(self.showImage)
        self.sig_live_on.connect(self.camera_worker.startAcquisition)
        self.sig_live_off.connect(self.camera_worker.abortAcquisition)
        self.sig_abort.connect(self.camera_worker.abortAcquisition)
        self.liveButton.clicked.connect(self.live)
        self.SnapButton.clicked.connect(self.snap)
        self.abortButton.clicked.connect(self.abort)

        self.liveTimer = QtCore.QTimer()
        self.liveTimer.timeout.connect(self.live_image)

    @QtCore.pyqtSlot()
    def live_image(self):
        # logger.info('camera window live image - signal')
        state = self.camera_worker.requestStatus()
        self.statusLabel.setText(state)
        if state == 'IDLE':
            self.sig_acquiredata.emit()
            self.sig_live_on.emit()

        
    @QtCore.pyqtSlot()
    def live(self):
        logger.info('handle live button - signal')
        if self.living:
            self.living = False
            self.liveButton.setText('live')
            self.sig_live_off.emit()
            self.liveTimer.stop()
        else:
            self.living = True
            self.liveButton.setText('stop')
            self.sig_live_on.emit()
            self.liveTimer.start(self.state['exposure_time'] * 1000)

    @QtCore.pyqtSlot()
    def snap(self):
        logger.info('snap an image - signal')
        self.snapping = True
        self.liveButton.setEnabled(False)
        self.sig_snap.emit()

    @QtCore.pyqtSlot()
    def abort(self):
        logger.info('abort camera imaging - signal')
        self.snapping = False
        self.liveButton.setEnabled(True)
        self.living = False
        self.liveButton.setText('live')
        self.liveTimer.stop()
        self.sig_abort.emit()

    @QtCore.pyqtSlot()
    def showImage(self):
        logger.info('camera window show image')
        self.image_view.setImage(self.state['npimage'], autoLevels=True, autoRange=True, autoHistogramRange=True)
    
    @QtCore.pyqtSlot()
    def updateStatus(self):
        # logger.info('update camera window status')
        if self.living:
            return
        state = self.state['cam_state']
        self.statusLabel.setText(state)
        if state == 'IDLE':
            if self.snapping:
                self.snapping = False
                self.liveButton.setEnabled(True)
                self.sig_acquiredata.emit()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    camera_window = camera_window()
    camera_window.show()
    sys.exit(app.exec())
