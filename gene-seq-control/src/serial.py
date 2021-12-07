"""
Serial
  control of the flowcell-related devices.

2021/12/06
"""

from PyQt5 import QtCore

from .devices.stm32.stm32_serial import stm32_serial
from .main_state import state_singleton

import time

import logging
logger = logging.getLogger(__name__)

class rcv_thread(QtCore.QThread):
    def __init__(self, ser, sig):
        super().__init__()
        self.ser = ser
        self.state = state_singleton()
        self.update_sig = sig

    def _check_is_changed_and_write(self, k, v):
        if self.state[k] == v:
            return False
        self.state[k] = v
        return True

    def run(self):
        while True:
            count = self.ser.inWaiting()
            if count != 0:
                rcv_cmd = self.ser.read(count)
                if count != 6:
                    continue
                if (rcv_cmd[0] == 0x55 and rcv_cmd[5] == 0xaa):
                    # Temperature
                    if (rcv_cmd[1] == 0x00):
                        flowcell_temperature = (rcv_cmd[3] + rcv_cmd[4] / 100)
                        if self._check_is_changed_and_write('flowcell_temperature', flowcell_temperature):
                            self.update_sig.emit('flowcell_temperature')

            time.sleep(0.1)

class serial(QtCore.QObject):
    _instance = None

    sig_state_flowcell_update = QtCore.pyqtSignal(str)

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = QtCore.QObject.__new__(cls, *args, **kw)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()

        self.flowcell = stm32_serial()

        self.state = state_singleton()

        self.rcv_thread = rcv_thread(self.flowcell.ser, self.sig_state_flowcell_update)

        self._initialized = True

    def __del__(self):
        try:
            self.rcv_thread.quit()

            self.rcv_thread.wait()
        except:
            pass

    def is_open(self):
        return self.flowcell.is_open()

    def open(self, comport):
        self.flowcell.connect(comport)

    def close(self):
        self.flowcell.close()

    def start_receive(self):
        self.rcv_thread.start()

    def stop_receive(self):
        self.rcv_thread.quit()

    def send_test_command(self):
        self.flowcell._send_command(b'\x55\x00\x00\x00\x00\xaa')

    def notify_all_state(self):
        self.sig_state_flowcell_update.emit('flowcell_temperature')