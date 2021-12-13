"""
Singleton Object represent platform state


2021/11/09
"""

import logging
logger = logging.getLogger(__name__)

from PyQt5 import QtCore

class state_singleton(QtCore.QObject):
    _instance = None

    sig_update_request = QtCore.pyqtSignal()

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = QtCore.QObject.__new__(cls, *args, **kw)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()

        self._state = {
            'z_pos': 0,
            'x_pos': 0,
            'y_pos': 0,
            'pfs_pos': 0,
            'tirf_pos': 0,
            'ftblock_pos': 0,
            'homed': False,
            'enabled': False,
            'tirf_inserted': False,
            'exposure_time': 0,
            'cam_temperature': 0,
            'em_gain': 0,
            'cam_cooler_state': '',
            'cam_state': '',
            'npimage': None,
            'flowcell_temperature': 0.0,
            'flowcell_valve_pos': 0,
            'flowcell_pump_valve_pos': 0,
            'flowcell_pump_pos': 0,
            'flowcell_pump_state': 0,
        }

        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.sig_update_request.emit)
        self.updateTimer.start(200)

        self._initialized = True

    def __getitem__(self, k):
        return self._state[k]

    def __setitem__(self, k, v):
        self._state[k] = v
