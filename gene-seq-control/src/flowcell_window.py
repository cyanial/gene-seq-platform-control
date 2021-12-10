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

    sig_valve_pos = QtCore.pyqtSignal(int)

    sig_pump_on_c = QtCore.pyqtSignal()
    sig_pump_off_c = QtCore.pyqtSignal()

    sig_pump_push_ul = QtCore.pyqtSignal(int)
    sig_pump_pull_ul = QtCore.pyqtSignal(int)

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

        self.valveGoButton.clicked.connect(self.valveGoToPos)
        self.sig_valve_pos.connect(self.flowcell_work.valveGoToPos)

        self.onCButton.clicked.connect(self.pump_on_c)
        self.sig_pump_on_c.connect(self.flowcell_work.pumpONC)
        self.onOFFButton.clicked.connect(self.pump_off_c)
        self.sig_pump_off_c.connect(self.flowcell_work.pumpOFFC)

        self.pushButton.clicked.connect(self.pump_push_ul)
        self.sig_pump_push_ul.connect(self.flowcell_work.pumpPushuL)
        self.pullButton.clicked.connect(self.pump_pull_ul)
        self.sig_pump_pull_ul.connect(self.flowcell_work.pumpPulluL)

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
        if k == 'flowcell_valve_pos':
            self.valvePosLabel.setText(str(self.state['flowcell_valve_pos']))
        if k == 'flowcell_pump_valve_pos':
            show_text = 'none'
            if self.state['flowcell_pump_valve_pos'] == 2:
                show_text = 'ON-C'
            elif self.state['flowcell_pump_valve_pos'] == 4:
                show_text = 'OFF-C'
            self.pumpValvePosLabel.setText(show_text)
        if k == 'flowcell_pump_pos':
            self.volumeProgressBar.setValue(int(self.state['flowcell_pump_pos']/120))

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

    @QtCore.pyqtSlot()
    def valveGoToPos(self):
        pos = int(self.valvePosChoose.currentText())
        self.sig_valve_pos.emit(pos)

    @QtCore.pyqtSlot()
    def pump_on_c(self):
        self.sig_pump_on_c.emit()

    @QtCore.pyqtSlot()
    def pump_off_c(self):
        self.sig_pump_off_c.emit()

    @QtCore.pyqtSlot()
    def pump_push_ul(self):
        ul = int(self.ulToPushOrPullLineEdit.text())
        self.sig_pump_push_ul.emit(ul)

    @QtCore.pyqtSlot()
    def pump_pull_ul(self):
        ul = int(self.ulToPushOrPullLineEdit.text())
        self.sig_pump_pull_ul.emit(ul)

    def _is_open(self):
        return self.flowcell_work.is_open();  

    def _scan_ports(self):
        self.comChooseList.clear()
        plist = list(list_ports.comports())
        for port in plist:
            self.comChooseList.addItem(port.name) 
    

