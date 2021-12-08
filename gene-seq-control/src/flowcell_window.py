"""
Flowcell Window
  reley on gui/flowcell_view.ui

2021/12/07
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog

from PyQt5.uic import loadUi

from serial.tools import list_ports

from .main_state import state_singleton
from .serial import serial

class flowcell_window(QDialog):

    sig_temp_on = QtCore.pyqtSignal()
    sig_temp_off = QtCore.pyqtSignal()

    sig_temp_set = QtCore.pyqtSignal(float)

    def __init__(self):
        super().__init__()
        loadUi('gui/flowcell_view.ui', self)
        self.flowcell_work = serial()
        self.state = state_singleton()
        self._scan_ports()

        self.refreshButton.clicked.connect(self.refresh_ports)
        self.connectButton.clicked.connect(self.connect)
        
        # Update Signal
        self.flowcell_work.sig_state_flowcell_update.connect(self.upadteStatus)

        # 
        self.setTemperatureButton.clicked.connect(self.setPIDTemperature)
        self.sig_temp_set.connect(self.flowcell_work.setup_temperature)
        self.tempPIDONButton.clicked.connect(self.tempPIDON)
        self.sig_temp_on.connect(self.flowcell_work.tempPIDON)
        self.tempPIDOFFButton.clicked.connect(self.tempPIDOFF)
        self.sig_temp_off.connect(self.flowcell_work.tempPIDOFF)

    @QtCore.pyqtSlot()
    def refresh_ports(self):
        self._scan_ports()

    @QtCore.pyqtSlot()
    def connect(self):
        if self._is_open():
            self.flowcell_work.stop_receive()
            self.flowcell_work.close() 
            self.connectButton.setText('Connect')
        else:
            try:
                comport = self.comChooseList.currentText()
                self.flowcell_work.open(comport)
                self.flowcell_work.start_receive()
                self.connectButton.setText('DisConn') 
            except:
                self.connectButton.setText('Connect')

    @QtCore.pyqtSlot(str)
    def upadteStatus(self, k):
        if k == 'flowcell_temperature':
            self.temperatureLabel.setText(str(round(self.state['flowcell_temperature'], 2)))

    @QtCore.pyqtSlot()
    def setPIDTemperature(self):
        setup_point = float(self.setupTemperature.text())
        self.sig_temp_set.emit(setup_point)

    @QtCore.pyqtSlot()
    def tempPIDON(self):
        self.sig_temp_on.emit()

    @QtCore.pyqtSlot()
    def tempPIDOFF(self):
        self.sig_temp_off.emit()

    def _is_open(self):
        return self.flowcell_work.is_open();  

    def _scan_ports(self):
        self.comChooseList.clear()
        plist = list(list_ports.comports())
        for port in plist:
            self.comChooseList.addItem(port.name) 
    

