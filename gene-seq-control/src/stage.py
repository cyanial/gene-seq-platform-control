"""
Stage 
  warp of low-level stage.
  run in an independent thread

2021/11/13
"""

from .devices.stage.thorlabs import Kinesis_Stage
from .main_state import state_singleton

from PyQt5 import QtCore

import logging
logger = logging.getLogger(__name__)

class stage(QtCore.QObject):
    _instance = None

    sig_state_stage_update = QtCore.pyqtSignal(str)

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = QtCore.QObject.__new__(cls, *args, **kw)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()

        self.stage = Kinesis_Stage()

        self.state = state_singleton()

        self._initialized = True

    def __del__(self):
        pass

    @QtCore.pyqtSlot()    
    def get_x_pos(self):
        if self._check_is_changed_and_write('x_pos', self.stage.getXpos()):
            self.sig_state_stage_update.emit('x_pos')

    @QtCore.pyqtSlot()
    def get_y_pos(self):
        if self._check_is_changed_and_write('y_pos', self.stage.getYpos()):
            self.sig_state_stage_update.emit('y_pos')

    @QtCore.pyqtSlot()
    def get_homed(self):
        if self._check_is_changed_and_write('homed', self.stage.isHomed()):
            self.sig_state_stage_update.emit('homed')

    @QtCore.pyqtSlot()
    def get_enabled(self):
        if self._check_is_changed_and_write('enabled', self.stage.isEnable()):
            self.sig_state_stage_update.emit('enabled')

    @QtCore.pyqtSlot()
    def updateStageState(self):
        self.get_x_pos()
        self.get_y_pos()
        self.get_homed()
        self.get_enabled()

    @QtCore.pyqtSlot()
    def enable(self):
        self.stage.enable()

    @QtCore.pyqtSlot()
    def disable(self):
        self.stage.disable()

    @QtCore.pyqtSlot()
    def home(self):
        self.stage.home()

    @QtCore.pyqtSlot(float, float)
    def moveAbsolute(self, x, y):
        self.stage.moveAbs_mm(x, y)

    @QtCore.pyqtSlot(float)
    def stepX(self, step):
        self.stage.moveXRel_mm(step)

    @QtCore.pyqtSlot(float)
    def stepY(self, step):
        self.stage.moveYRel_mm(step)

    def xpos_to_mm(self, xpos):
        return self.stage.xpos_to_mm(xpos)

    def ypos_to_mm(self, ypos):
        return self.stage.ypos_to_mm(ypos)

    def _check_is_changed_and_write(self, k, v):
        if self.state[k] == v:
            return False
        self.state[k] = v
        return True

    def notify_all_state(self):
        self.sig_state_stage_update.emit('x_pos')
        self.sig_state_stage_update.emit('y_pos')
        self.sig_state_stage_update.emit('homed')
        self.sig_state_stage_update.emit('enabled')
