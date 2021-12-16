"""
Camera Window 
  reley on gui/camera
           device/camera

2021/11/08

"""

from .devices.microscope.nikonti import nikonTi
from .main_state import state_singleton

from PyQt5 import QtCore

import logging
logger = logging.getLogger(__name__)

class microscope(QtCore.QObject):
    _instance = None

    sig_state_microscope_update = QtCore.pyqtSignal(str)

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = QtCore.QObject.__new__(cls, *args, **kw)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        
        self.mic = nikonTi()

        self.state = state_singleton()

        self._initialized = True

    def __del__(self):
        pass

    @QtCore.pyqtSlot()
    def get_ftblock_pos(self):
        # logger.info('get mic filter block pos')
        if self._check_is_changed_and_write('ftblock_pos', self.mic.ftblock_pos()):
            self.sig_state_microscope_update.emit('ftblock_pos')

    @QtCore.pyqtSlot()
    def get_z_pos(self):
        # logger.info('get mic z pos')
        if self._check_is_changed_and_write('z_pos', self.mic.zPos()):
            self.sig_state_microscope_update.emit('z_pos')

    QtCore.pyqtSlot()
    def get_pfs_pos(self):
        # logger.info('get mic pfs pos')
        if self._check_is_changed_and_write('pfs_pos', self.mic.pfsPos()):
            self.sig_state_microscope_update.emit('pfs_pos')

    @QtCore.pyqtSlot()
    def get_tirf_pos(self):
        # logger.info('get mic tirf pos')
        if self._check_is_changed_and_write('tirf_pos', self.mic.tirfPos()):
            self.sig_state_microscope_update.emit('tirf_pos')

    @QtCore.pyqtSlot()
    def get_tirf_inserted(self):
        # logger.info('get mic tirf inserted')
        if self._check_is_changed_and_write('tirf_inserted', self.mic.tirfIsInserted()):
            self.sig_state_microscope_update.emit('tirf_inserted')

    @QtCore.pyqtSlot()
    def updateMicroscopeState(self):
        # logger.info('update mic state')
        self.get_z_pos()
        self.get_pfs_pos()
        self.get_tirf_pos()
        self.get_tirf_inserted()
        self.get_ftblock_pos()

    @QtCore.pyqtSlot()
    def insertTirf(self):
        logger.info('mic insert tirf')
        self.mic.tirfInsert()

    @QtCore.pyqtSlot()
    def extractTirf(self):
        logger.info('mic extract tirf')
        self.mic.tirfExtract()

    @QtCore.pyqtSlot(int)
    def tirfStep(self, step):
        logger.info(f'mic tirf move relative {step} step(s)')
        self.mic.tirfMoveRealtive(step)

    @QtCore.pyqtSlot(int)
    def openShutter(self, shutterID):
        logger.info(f'mic open shutter {shutterID}')
        self.mic.shutterOpenAndCloseOthers(shutterID)

    @QtCore.pyqtSlot()
    def closeAllShutter(self):
        logger.info(f'mic close all shutters')
        self.mic.closeAllShutter()

    @QtCore.pyqtSlot()
    def filterBlockForward(self):
        logger.info('mic filter block forward')
        self.mic.ftblock_forward()

    @QtCore.pyqtSlot()
    def filterBlockReverse(self):
        logger.info('mic filter block reverse')
        self.mic.ftblock_reverse()

    @QtCore.pyqtSlot(int)
    def filterBlockMoveToPos(self, pos):
        logger.info(f'mic filter block move to pos {pos}')
        self.mic.ftblock_move_to_pos(pos)
        
    def zpos_to_um(self, zpos):
        return self.mic.zpos_to_um(zpos)

    def _check_is_changed_and_write(self, k, v):
        if self.state[k] == v:
            return False
        self.state[k] = v
        return True

    def notify_all_state(self):
        self.sig_state_microscope_update.emit('z_pos')
        self.sig_state_microscope_update.emit('pfs_pos')
        self.sig_state_microscope_update.emit('tirf_pos')
        self.sig_state_microscope_update.emit('tirf_inserted')
        self.sig_state_microscope_update.emit('ftblock_pos')
