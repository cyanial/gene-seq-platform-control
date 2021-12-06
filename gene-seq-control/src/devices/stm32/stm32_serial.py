"""
STM32 Serial

2021/12/06
"""

import serial
# import io

from PyQt5 import QtCore

class stm32_serial(QtCore.QObject):

    def __init__(self, COMport, baudrate):
        super().__init__()

        self.COMport = COMport
        self.baudrate = baudrate
        self.ser = None
        # self.sio = None
        self._connect()

    def __del__(self):
        # self.sio.flush()
        self.ser.close()

    def _connect(self):
        """
        Connect serial
        """
        try:
            self.ser = serial.Serial(self.COMport,
                                    self.baudrate,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    timeout=0,
                                    write_timeout=0,
                                    xonxoff=False,
                                    stopbits=serial.STOPBITS_ONE)
            # self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        except serial.SerialException as e:
            print(f"ERROR: Serial Connection to stm32 failed: {e}")

