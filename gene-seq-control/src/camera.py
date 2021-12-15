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

        logger.debug('create camera object')

        self.camera = Andor_EMCCD()

        self.state = state_singleton()

        self._initialized = True

    def __del__(self):
        pass

    @QtCore.pyqtSlot(float)
    def setExposureTime(self, t):
        logger.info('set camera exposure time')
        real_t = self.camera.setExposureTime(t)
        self.state['exposure_time'] = real_t
        self.sig_state_camera_update.emit('exposure_time')

    @QtCore.pyqtSlot()
    def getTemperature(self):
        # logger.info('get camerea temperature')
        cam_t, cooler_state = self.camera.getTemperature()
        if self._check_is_changed_and_write('cam_temperature', cam_t):
            self.sig_state_camera_update.emit('cam_temperature')
        if self._check_is_changed_and_write('cam_cooler_state', cooler_state):
            self.sig_state_camera_update.emit('cam_cooler_state')

    @QtCore.pyqtSlot(int)
    def setTemperature(self, t):
        logger.info(f'set camera temperature - {t}')
        self.camera.setTemperature(t)

    @QtCore.pyqtSlot()
    def getStatus(self):
        # logger.info('get camera status')
        cam_state = self.camera.getStatus()
        if self._check_is_changed_and_write('cam_state', cam_state):
            self.sig_state_camera_status.emit()

    @QtCore.pyqtSlot()
    def getEMGain(self):
        # logger.info('get camera em gain')
        em = self.camera.getEMGain()
        if self._check_is_changed_and_write('em_gain', em):
            self.sig_state_camera_update.emit('em_gain')

    @QtCore.pyqtSlot(int)
    def setEMGain(self, gain):
        logger.info(f'set camera em gain - {gain}')
        self.camera.setEMGain(gain)

    @QtCore.pyqtSlot()
    def coolerON(self):
        logger.info('set camera cooler on')
        self.camera.coolerON()

    @QtCore.pyqtSlot()
    def coolerOFF(self):
        logger.info('set camera cooler off')
        self.camera.coolerOFF()

    @QtCore.pyqtSlot()
    def fanHigh(self):
        logger.info('set camera fan high')
        self.camera.fanFullSpeed()

    @QtCore.pyqtSlot()
    def fanLow(self):
        logger.info('set camera fan low')
        self.camera.fanLowSpeed()

    @QtCore.pyqtSlot()
    def fanOff(self):
        logger.info('set camera fan off')
        self.camera.fanOFF()

    @QtCore.pyqtSlot()
    def requestStatus(self):
        # logger.info('get camera status')
        return self.camera.getStatus()

    @QtCore.pyqtSlot()
    def acquireData(self):
        logger.info('acquire camera data')
        self.state['npimage'] = self.camera.acquireData()
        self.sig_image_data_ready.emit()

    @QtCore.pyqtSlot()
    def startAcquisition(self):
        logger.info('start camera acquisition')
        self.camera.startAcquisition()

    @QtCore.pyqtSlot()
    def abortAcquisition(self):
        logger.info('abort camera acquisition')
        self.camera.abortAcquisition()

    @QtCore.pyqtSlot()
    def updateCameraState(self):
        # logger.info('update camera state')
        self.getTemperature()
        self.getEMGain()
        self.getStatus()

    def _check_is_changed_and_write(self, k, v):
        if self.state[k] == v:
            return False
        self.state[k] = v
        return True

    def notify_all_state(self):
        self.sig_state_camera_update.emit('exposure_time')
        self.sig_state_camera_update.emit('cam_temperature')
        self.sig_state_camera_update.emit('cam_cooler_state')
        self.sig_state_camera_update.emit('em_gain')
        self.sig_state_camera_status.emit()