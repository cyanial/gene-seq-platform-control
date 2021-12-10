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
                if count != 9:
                    continue
                if (rcv_cmd[0] == 0x55 and rcv_cmd[8] == 0xaa):
                    # Temperature
                    if self._check_is_changed_and_write('flowcell_temperature', (rcv_cmd[1] + rcv_cmd[2] / 100)):
                        self.update_sig.emit('flowcell_temperature')
                    # Valve Pos
                    if self._check_is_changed_and_write('flowcell_valve_pos', int(rcv_cmd[3])):
                        self.update_sig.emit('flowcell_valve_pos')
                    # Pump Valve Pos
                    if self._check_is_changed_and_write('flowcell_pump_valve_pos', int(rcv_cmd[4])):
                        self.update_sig.emit('flowcell_pump_valve_pos')
                    # Pump Pos
                    if self._check_is_changed_and_write('flowcell_pump_pos', int(rcv_cmd[5] << 8) + int(rcv_cmd[6])):
                        self.update_sig.emit('flowcell_pump_pos')
                    # Pump State
                    if self._check_is_changed_and_write('flowcell_pump_state', int (rcv_cmd[7])):
                        self.update_sig.emit('flowcell_pump_state')
                #     # Temperature
                #     if (rcv_cmd[1] == 0x00):
                #         if (rcv_cmd[2] == 0x00):
                #             flowcell_temperature = (rcv_cmd[3] + rcv_cmd[4] / 100)
                #             if self._check_is_changed_and_write('flowcell_temperature', flowcell_temperature):
                #                 self.update_sig.emit('flowcell_temperature')
                #     # Valve Pos
                #     if (rcv_cmd[1] == 0x02):
                #         if (rcv_cmd[2] == 0x00):
                #             if self._check_is_changed_and_write('flowcell_valve_pos', int(rcv_cmd[4])):
                #                 self.update_sig.emit('flowcell_valve_pos')
                #     # Pump Valve Pos
                #     if (rcv_cmd[1] == 0x01):
                #         if (rcv_cmd[2] == 0x00):
                #             if self._check_is_changed_and_write('flowcell_pump_valve_pos', int(rcv_cmd[4])):
                #                 self.update_sig.emit('flowcell_pump_valve_pos')
                #         if (rcv_cmd[2] == 0x03):
                #             step_pos = int(rcv_cmd[3] << 8) + int(rcv_cmd[4])
                #             if self._check_is_changed_and_write('flowcell_pump_pos', step_pos):
                #                 self.update_sig.emit('flowcell_pump_pos')

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

    @QtCore.pyqtSlot(float)
    def setup_temperature(self, setup_point):
        self.flowcell.set_temp_pid(setup_point)

    @QtCore.pyqtSlot()
    def tempPIDON(self):
        self.flowcell.start_temp_pid()

    @QtCore.pyqtSlot()
    def tempPIDOFF(self):
        self.flowcell.stop_temp_pid()

    @QtCore.pyqtSlot(int)
    def valveGoToPos(self, pos):
        self.flowcell.valve_to_pos(pos)

    @QtCore.pyqtSlot()
    def pumpONC(self):
        self.flowcell.pump_on_c()

    @QtCore.pyqtSlot()
    def pumpOFFC(self):
        self.flowcell.pump_on_off()

    @QtCore.pyqtSlot(int)
    def pumpPushuL(self, ul):
        self.flowcell.pump_push_ul(ul)

    @QtCore.pyqtSlot(int)
    def pumpPulluL(self, ul):
        self.flowcell.pump_pull_ul(ul)

    def send_test_command(self):
        self.flowcell._send_command(b'\x55\x00\x00\x00\x00\xaa')

    def notify_all_state(self):
        self.sig_state_flowcell_update.emit('flowcell_temperature')
        self.sig_state_flowcell_update.emit('flowcell_valve_pos')
        self.sig_state_flowcell_update.emit('flowcell_pump_valve_pos')
        self.sig_state_flowcell_update.emit('flowcell_pump_pos')
        self.sig_state_flowcell_update.emit('flowcell_pump_state')