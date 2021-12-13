"""
Seq Manager Window
  2021/11/13

"""

import os
import time

from PyQt5 import QtCore
import PyQt5

from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer

import tifffile

from .main_state import state_singleton
from .camera import camera
from .microscope import microscope
from .serial import serial
from .stage import stage

import logging
logger = logging.getLogger(__name__)


class seq_manager(QDialog):

    # Run_state:
    # 'idle':
    # 'running':
    #   - 'prolong': 
    #   - 'washing':
    #   - 'imaging':
    # 'pause':

    # 7 4
    seq_x_pos = [35, 40, 45, 50, 55, 60, 75]
    seq_y_pos = [36.5, 37.0, 38.5, 39.0]
    
    def __init__(self):
        super().__init__()
        self.state = state_singleton()
        loadUi('gui/seq_manager.ui', self)

        self._set_output_folder(os.getcwd() + '\\out')
        self.camera = camera()
        self.mic = microscope()
        self.flowcell = serial()
        self.stage = stage()

        self.run_state = 'idle'
        self._set_current_state(self.run_state)
        self.run_task = 'no task'
        self._set_current_task(self.run_task)

        self.workTimer = QTimer()
        self.prolongWaitTimer = QTimer()
        self.washWorkTimer = QTimer()
        self.imagingWorkTimer = QTimer()

        self.workTimer.timeout.connect(self.worker)
        self.prolongWaitTimer.timeout.connect(self.waitProlongTask)
        self.washWorkTimer.timeout.connect(self.washTask)
        self.imagingWorkTimer.timeout.connect(self.imagingWork)

        self.outputFolderButton.clicked.connect(self.chooseDirctory)
        self.startSeqButton.clicked.connect(self.startSeq)

    @QtCore.pyqtSlot()
    def startSeq(self):
        self.run_state = 'running'
        self._set_current_state(self.run_state)
        self.idx_x = 0
        self.idx_y = 0
        self.flowcell.pump_push_all()
        self.workTimer.start(1000)

    @QtCore.pyqtSlot()
    def worker(self): 
        self.workTimer.stop()
        # Prolong:
        self.run_task = 'prolong'
        self._set_current_task(self.run_task)
        
        # Pull
        if self.state['flowcell_pump_pos'] > 10000:
            self.flowcell.pump_push_all()
        time.sleep(2)
        self.flowcell.pumpONC()
        while self.state['flowcell_pump_valve_pos'] != 2:
            print("Wait Pump Valve to ON-C")
        self.flowcell.valveGoToPos(1)
        while self.state['flowcell_valve_pos'] != 1:
            print("Wait Valve pos to 1")
        print("Valve Pump OK")
        self.flowcell.pumpPulluL(200)
        time.sleep(1)
        while self.state['flowcell_pump_state'] != 0:
            pass
        print('Pump Pull OK')
        self.prolongCurrentSecond = 0
        self.prolongAllSecond = 30
        self.prolongWaitTimer.start(1000)
        # Wait for time: (15 min) 30s for test

        
    @QtCore.pyqtSlot()
    def waitProlongTask(self):
        if self.prolongCurrentSecond == self.prolongAllSecond:
            self.prolongWaitTimer.stop()
            self.currentTaskProgressBar.setValue(0)
            self.flowcell.pump_push_all()
            self.washingAllTimes = 3
            self.currentWashTime = 0
            self.run_task = f'washing - {self.currentWashTime}/{self.washingAllTimes}'
            self._set_current_task(self.run_task)
            self.washWorkTimer.start(1000)
            return
        self.prolongCurrentSecond = self.prolongCurrentSecond + 1
        self.run_task = f'prolong - {self.prolongCurrentSecond}/{self.prolongAllSecond} sec(s)'
        self._set_current_task(self.run_task)
        self.currentTaskProgressBar.setValue(int(self.prolongCurrentSecond/self.prolongAllSecond*100))

    @QtCore.pyqtSlot()
    def washTask(self):
        # Wash 3 times
        self.washWorkTimer.stop()
        if self.currentWashTime == self.washingAllTimes:
            # Washing Done 
            # Start imaging
            self.idx_x = 0
            self.idx_y = 0
            self.idx_x_sum = len(self.seq_x_pos)
            self.idx_y_sum = len(self.seq_y_pos)
            self.currentTaskProgressBar.setValue(0)
            # self.stage.moveAbsolute(self.seq_x_pos[], self.seq_y_pos[])
            self.run_task = f'imaging - x: {self.seq_x_pos[self.idx_x]} y:{self.seq_y_pos[self.idx_y]}'
            self._set_current_task(self.run_task)
            self.imagingWorkTimer.start(1000)
            return
        self.currentWashTime = self.currentWashTime + 1
        self.run_task = f'washing - {self.currentWashTime}/{self.washingAllTimes}'
        self._set_current_task(self.run_task)
        self.currentTaskProgressBar.setValue(int(self.currentWashTime/self.washingAllTimes*100))
        self.flowcell.pumpONC()
        while self.state['flowcell_pump_valve_pos'] != 2:
            print("Wait Pump Valve to ON-C")
        self.flowcell.valveGoToPos(2)
        while self.state['flowcell_valve_pos'] != 2:
            print("Wait Valve pos to 2")
        print("Valve Pump OK")
        self.flowcell.pumpPulluL(200)
        time.sleep(1)
        while self.state['flowcell_pump_state'] != 0:
            pass
        print('Pump Pull OK')
        self.washWorkTimer.start(1000)
        
    @QtCore.pyqtSlot()
    def imagingWork(self):
        self.imagingWorkTimer.stop()
        self.stage.moveAbsolute(self.seq_x_pos[self.idx_x], self.seq_y_pos[self.idx_y])
        time.sleep(3)
        # A C T G
        # Choose Filter
        # Open Shutter
        # Imaging - - - -
        for i in range(1, 5):
            while self.state['ftblock_pos'] != i:
                if self.state['ftblock_pos'] > i:
                    self.mic.filterBlockReverse()
                else:
                    self.mic.filterBlockForward()
                QtCore.QThread.sleep(1)
            self.mic.openShutter(i)
            self.camera.startAcquisition()
            print(f"Imaging: Shutter{i} - pos: {self.idx_x}, {self.idx_y}")
            time.sleep(self.state['exposure_time'])
            while self.state['cam_state'] != 'IDLE':
                print(self.state['cam_state'])
            self.mic.closeAllShutter()
            self.state['npimage'] = self.camera.camera.acquireData()
            time.sleep(1)
            # Save Files to output folder (filename)
            tifffile.imsave(self.output_folder + f'\\shutter{i}_pos_{self.idx_x}_{self.idx_y}_timestr.tif', self.state['npimage'])

        self.idx_x = self.idx_x + 1
        if self.idx_x == self.idx_x_sum:
            self.idx_y = self.idx_y + 1
            if self.idx_y == self.idx_y_sum:
                # Do next cycle
                print('Imaging Done')
                return
            self.idx_x = 0
        self.currentTaskProgressBar.setValue(int((self.idx_x + self.idx_x_sum * self.idx_y) / (self.idx_x_sum * self.idx_y_sum) * 100))
        self.run_task = f'imaging - x: {self.seq_x_pos[self.idx_x]} y:{self.seq_y_pos[self.idx_y]}'
        self._set_current_task(self.run_task)
        self.imagingWorkTimer.start(1000)
            
        
    @QtCore.pyqtSlot()
    def chooseDirctory(self):
        dir_choose = QFileDialog.getExistingDirectory(self, 'Choose output folder', self.output_folder)
        self._set_output_folder(dir_choose)

    def _set_output_folder(self, foldername):
        self.output_folder = foldername
        self.outputfolder.setText(foldername)

    def _set_current_state(self, state_text):
        self.seqStateLabel.setText(state_text)

    def _set_current_task(self, task_name):
        self.currentTaskName.setText(task_name)
    
    

