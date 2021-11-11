"""
Singleton Object represent platform state


2021/11/09
"""

import logging
logger = logging.getLogger(__name__)

from PyQt5 import QtCore

from .devices.microscope.nikonti import nikonTi
from .devices.stage.thorlabs import Kinesis_Stage
from .devices.camera.andor import Andor_EMCCD

class state_singleton(QtCore.QObject):
    _instance = None

    sig_state_updated = QtCore.pyqtSignal(str)


    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = QtCore.QObject.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        super().__init__()
        self._microscope = nikonTi()
        self._stage = Kinesis_Stage()
        self._camera = Andor_EMCCD()

        self._state = {
            'z_pos': 0,
            'x_pos': 0,
            'y_pos': 0,
            'pfs_pos': 0,
            'tirf_pos': 0,
            'homed': False,
            'enabled': False,
            'tirf_inserted': False,
            'exposure_time': 0,
            'cam_temperature': 0,
            'cam_cooler_state': '',
            'cam_state': '',
        }

        self._notify_all_state()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateStateSlot)
        self.timer.start(200)

    def camTemperature(self):
        return self._state['cam_temperature']

    def camCoolerState(self):
        return self._state['cam_cooler_state']

    def camState(self):
        return self._state['cam_state']

    def exposureTime(self):
        return self._state['exposure_time']

    def tirfInserted(self):
        return self._state['tirf_inserted']

    def isHomed(self):
        return self._state['homed']

    def isEnabled(self):
        return self._state['enabled']

    def tirfPos(self):
        return self._state['tirf_pos']

    def pfsPos(self):
        return self._state['pfs_pos']

    def zpos_to_um(self):
        return self._microscope.zpos_to_um(self._state['z_pos'])

    def xpos_to_mm(self):
        return self._stage.xpos_to_mm(self._state['x_pos'])

    def ypos_to_mm(self):
        return self._stage.ypos_to_mm(self._state['y_pos'])

    def getState(self):
        return self._state

    def getMicroscope(self):
        return self._microscope

    def getStage(self):
        return self._stage

    def getCamera(self):
        return self._camera

    def setExposureTime(self, time):
        real_time = self.getCamera().setExposureTime(time)
        self._state['exposure_time'] = real_time
        print(real_time)
        self.sig_state_updated.emit('exposure_time')

    def updateStateSlot(self):
        self._check_state_value('z_pos', self.getMicroscope().zGetPos())
        self._check_state_value('x_pos', self.getStage().getXpos())
        self._check_state_value('y_pos', self.getStage().getYpos())
        self._check_state_value('pfs_pos', self.getMicroscope().pfsPos())
        self._check_state_value('tirf_pos', self.getMicroscope().tirfPos())
        self._check_state_value('homed', self.getStage().isHomed())
        self._check_state_value('enabled', self.getStage().isEnable())
        self._check_state_value('tirf_inserted', self.getMicroscope().tirfIsInserted())
        cam_temp, cam_cooler = self.getCamera().getTemperature()
        self._check_state_value('cam_temperature', cam_temp)
        self._check_state_value('cam_cooler_state', cam_cooler)
        self._check_state_value('cam_state', self.getCamera().getStatus())

    def _check_state_value(self, item, value):
        if self._state[item] != value:
            self._state[item] = value
            self.sig_state_updated.emit(item)

    def _notify_all_state(self):
        for k in self._state.keys():
            self.sig_state_updated.emit(k)
        
        

