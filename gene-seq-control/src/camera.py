"""
Camera 
  warp of low-level camera.
  run in an independent thread

2021/11/13
"""

from .devices.camera.andor import Andor_EMCCD
from .main_state import state_singleton

from PyQt5 import QtCore

import logging
logger = logging.getLogger(__name__)


class camera(QtCore.QObject):
    _instance = None

    sig_state_camera_update = QtCore.pyqtSignal(str)
    sig_state_camera_status = QtCore.pyqtSignal()
    sig_image_data_ready = QtCore.pyqtSignal()

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = QtCore.QObject.__new__(cls, *args, **kw)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()

        self.camera = Andor_EMCCD()

        self.state = state_singleton()

        self._initialized = True

    def __del__(self):
        pass

    @QtCore.pyqtSlot(float)
    def setExposureTime(self, t):
        real_t = self.camera.setExposureTime(t)
        self.state['exposure_time'] = real_t
        self.sig_state_camera_update.emit('exposure_time')

    @QtCore.pyqtSlot()
    def getTemperature(self):
        cam_t, cooler_state = self.camera.getTemperature()
        if self._check_is_changed_and_write('cam_temperature', cam_t):
            self.sig_state_camera_update.emit('cam_temperature')
        if self._check_is_changed_and_write('cam_cooler_state', cooler_state):
            self.sig_state_camera_update.emit('cam_cooler_state')

    @QtCore.pyqtSlot(int)
    def setTemperature(self, t):
        self.camera.setTemperature(t)

    @QtCore.pyqtSlot()
    def getStatus(self):
        cam_state = self.camera.getStatus()
        if self._check_is_changed_and_write('cam_state', cam_state):
            self.sig_state_camera_status.emit()

    @QtCore.pyqtSlot()
    def getEMGain(self):
        em = self.camera.getEMGain()
        if self._check_is_changed_and_write('em_gain', em):
            self.sig_state_camera_update.emit('em_gain')

    @QtCore.pyqtSlot(int)
    def setEMGain(self, gain):
        self.camera.setEMGain(gain)

    @QtCore.pyqtSlot()
    def coolerON(self):
        self.camera.coolerON()

    @QtCore.pyqtSlot()
    def coolerOFF(self):
        self.camera.coolerOFF()

    @QtCore.pyqtSlot()
    def fanHigh(self):
        self.camera.fanFullSpeed()

    @QtCore.pyqtSlot()
    def fanLow(self):
        self.camera.fanLowSpeed()

    @QtCore.pyqtSlot()
    def fanOff(self):
        self.camera.fanOFF()

    @QtCore.pyqtSlot()
    def updateCameraState(self):
        self.getTemperature()
        self.getEMGain()
        self.getStatus()

    @QtCore.pyqtSlot()
    def requestStatus(self):
        return self.camera.getStatus()

    @QtCore.pyqtSlot()
    def acquireData(self):
        self.state['npimage'] = self.camera.acquireData()
        self.sig_image_data_ready.emit()

    @QtCore.pyqtSlot()
    def startAcquisition(self):
        self.camera.startAcquisition()

    @QtCore.pyqtSlot()
    def abortAcquisition(self):
        self.camera.abortAcquisition()

    def _check_is_changed_and_write(self, k, v):
        if self.state[k] == v:
            return False
        self.state[k] = v
        return True

    def notify_all_state(self):
        self.sig_state_camera_update.emit('exposure_time')
        self.sig_state_camera_update.emit('cam_temperature')
        self.sig_state_camera_update.emit('cam_cooler_state')
        self.sig_state_camera_status.emit()
        self.sig_state_camera_update.emit('em_gain')