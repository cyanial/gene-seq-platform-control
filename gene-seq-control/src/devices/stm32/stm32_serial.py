"""
STM32 Serial

2021/12/06
"""

import serial

from PyQt5 import QtCore

class stm32_serial(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.ser = serial.Serial()
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.timeout = 0
        self.ser.writeTimeout = 0
        self.ser.xonxoff = False
        self.ser.stopbits = serial.STOPBITS_ONE

        # self.rcv_thread = rcv_thread(self.ser)
        # self.rcv_thread.start()

    def __del__(self):
        self.ser.close()
        print('Shutdown - Flowcell')

    def connect(self, comport, baudrate=115200):
        self.ser.port = comport
        self.ser.baudrate = baudrate
        self.ser.open()

    def close(self):
        self.ser.close()

    def start_temp_pid(self):
        self._send_command(b'\x55\x00\x02\x00\x00\xaa')

    def stop_temp_pid(self):
        self._send_command(b'\x55\x00\x03\x00\x00\xaa')

    def set_temp_pid(self, setpoint):
        real = int(setpoint)
        frac = int((setpoint-real)*100) % 100
        cmd = bytearray(b'\x55\x00\x01\x00\x00\xaa')
        cmd[3] = real
        cmd[4] = frac
        self._send_command(cmd)

    def valve_to_pos(self, pos):
        cmd = bytearray(b'\x55\x02\x00\x00\x00\xaa')
        cmd[4] = pos
        self._send_command(cmd)

    def pump_on_c(self):
        self._send_command(b'\x55\x01\x00\x00\x02\xaa')

    def pump_on_off(self):
        self._send_command(b'\x55\x01\x00\x00\x04\xaa')

    def pump_push_ul(self, ul):
        cmd = bytearray(b'\x55\x01\x02\x00\x00\xaa')
        cmd[3] = (ul >> 8)
        cmd[4] = (ul & 0xff)
        self._send_command(cmd)

    def pump_pull_ul(self, ul):
        cmd = bytearray(b'\x55\x01\x01\x00\x00\xaa')
        cmd[3] = (ul >> 8)
        cmd[4] = (ul & 0xff)
        self._send_command(cmd)

    def _send_command(self, command):
        # Command example: b'\x55\x00\x00\x00\x00\xaa'
        self.ser.write(command)

    def receive_command(self):
        pass

    def is_open(self):
        return self.ser.is_open
                


