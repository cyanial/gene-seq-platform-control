"""
Seq Manager Window
  2021/11/13

"""

import os
import time
from datetime import datetime

from PyQt5 import QtCore

from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi

import tifffile

from .main_state import state_singleton
from .camera import camera
from .microscope import microscope
from .serial import serial
from .stage import stage

import logging
logger = logging.getLogger(__name__)


# Run_state:
#     'idle':
#     'running' - cycle 1/max:
#       - 'pump push all':
#       - 'prolong': 
#       - 'washing':
#       - 'imaging':
#     'pause':

seq_state = {
    'run_state': 'idle',
    'run_task': 'no task',
    'total_cycle': 5,
    'current_cycle': 0,
    # 'seq_x_pos': [35, 40, 45, 50, 55, 60, 65, 70, 75],
    'seq_x_pos': [40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70],
    'seq_y_pos': [36.9, 37.2, 37.5, 37.8, 38.1, 38.4],
    'output_folder': '',
    'current_seq_folder_name': ''
}

class seq_task(QtCore.QThread):
    
    sig_update_run_state = QtCore.pyqtSignal()
    sig_update_task_state = QtCore.pyqtSignal()

    sig_update_task_progress_bar = QtCore.pyqtSignal(int, int)

    sig_mic_filter_block_move = QtCore.pyqtSignal(int)

    sig_mic_shutter_open = QtCore.pyqtSignal(int)

    sig_mic_close_all_shutter = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.state = state_singleton()
        self.camera = camera()
        self.mic = microscope()
        self.flowcell = serial()
        self.stage = stage()

        self.sig_mic_filter_block_move.connect(self.mic.filterBlockMoveToPos)
        self.sig_mic_shutter_open.connect(self.mic.openShutter)
        self.sig_mic_close_all_shutter.connect(self.mic.closeAllShutter)
        self.wait_sec = 0

    def _update_run_state(self, state):
        seq_state['run_state'] = state
        self.sig_update_run_state.emit()

    def _update_task_state(self, task_name):
        seq_state['run_task'] = task_name
        self.sig_update_task_state.emit()

    def run(self):
        os.makedirs(seq_state['current_seq_folder_name'] + '\\' + str(seq_state['current_cycle']))
        logger.info('run seq task')
        self._update_run_state('running')
        self._update_task_state('pump: push all')
        self.flowcell.pump_push_all()
        
        self._update_task_state('prolong: ')
        if self.state['flowcell_pump_pos'] > 10000:
            self._update_task_state('prolong: pump push all')
        time.sleep(1)
        # self.sleep(1)

        # Prolong Task
        self._update_task_state("prolong: pump valve -> on-c")
        self.flowcell.pumpONC()
        while self.state['flowcell_pump_valve_pos'] != 2:
            pass
        self._update_task_state("prolong: valve -> 1")
        self.flowcell.valveGoToPos(1)
        while self.state['flowcell_valve_pos'] != 1:
            pass
        self._update_task_state("prolong: pump pull 200 uL")
        self.flowcell.pumpPulluL(200)
        time.sleep(1)
        while self.state['flowcell_pump_state'] != 0:
            pass
        self.sig_update_task_progress_bar.emit(0, 30)
        while self.wait_sec != 30:
            self._update_task_state(f"prolong: wait {self.wait_sec}/30 sec")
            time.sleep(1)
            self.wait_sec = self.wait_sec + 1
            self.sig_update_task_progress_bar.emit(self.wait_sec, 30)
        self.wait_sec = 0
        
        # Wash Task
        self._update_task_state('washing: pump valve -> on-c')
        self.flowcell.pumpONC()
        while self.state['flowcell_pump_valve_pos'] != 2:
            pass
        self._update_task_state('washing: valve -> 2')
        self.flowcell.valveGoToPos(2)
        while self.state['flowcell_valve_pos'] != 2:
           pass
        self._update_task_state('washing: 1/3')
        self.sig_update_task_progress_bar.emit(1, 3)
        for i in range(3):
            self.flowcell.pumpPulluL(200)
            time.sleep(1)
            while self.state['flowcell_pump_state'] != 0:
                pass
            self._update_task_state(f'washing: {i+2}/3')
            self.sig_update_task_progress_bar.emit(i+2, 3)

        # self._update_task_state('washing: done')
        # self.sig_update_task_progress_bar.emit(0, 3)

        # Image Task
        self._update_task_state('imaging: ')

        x_len = len(seq_state['seq_x_pos'])
        y_len = len(seq_state['seq_y_pos'])
        # A C T G - Shutter 1 -> 2 -> 3 -> 4
        # Choose Filter -> Open Shutter -> Imaging -> Close Shutter -> Save Image
        for i in range(1, 5):
            while self.state['ftblock_pos'] != i:
                self._update_task_state(f'imaging: filter block -> {i}')
                self.sig_mic_filter_block_move.emit(i)
                time.sleep(1)
            for x in range(x_len):
                for y in range(y_len):
                    self.sig_update_task_progress_bar.emit(y+y_len*x+x_len*y_len*(i-1), x_len*y_len*4-1)
                    # Move Stages -> (x,y)
                    self._update_task_state(f'imaging: ({x},{y},{i}) stage moving ...')
                    self.stage.moveAbsolute(seq_state['seq_x_pos'][x], seq_state['seq_y_pos'][y])
                    time.sleep(1)
                    # Open Shutter
                    self._update_task_state(f'imaging: ({x},{y},{i}) open shutter')
                    self.sig_mic_shutter_open.emit(i)
                    # Start Acquisition
                    self.camera.startAcquisition()
                    self._update_task_state(f'imaging: ({x},{y},{i}) imaging ...')
                    time.sleep(self.state['exposure_time'])
                    while self.state['cam_state'] != 'IDLE':
                        pass
                    # Close Shutter
                    self.sig_mic_close_all_shutter.emit()
                    # Acquiring data
                    self._update_task_state(f'imaging: ({x},{y},{i}) acquiring data ...')
                    self.state['npimage'] = self.camera.camera.acquireData()
                    self.camera.sig_image_data_ready.emit()
                    time.sleep(0.5)
                    self._update_task_state(f'imaging: ({x},{y},{i}) save image to file ...')
                    tifffile.imsave(seq_state['current_seq_folder_name'] + '\\' + str(seq_state['current_cycle']) + f'\\pos_{x}_{y}_shutter{i}.tif', self.state['npimage'])
        print('Done')

        # for x in range(x_len):
        #     for y in range(y_len):
        #         self.sig_update_task_progress_bar.emit(y+y_len*x, x_len*y_len-1)
        #         self._update_task_state(f'imaging: stage move to ({x},{y})')
        #         self.stage.moveAbsolute(seq_state['seq_x_pos'][x], seq_state['seq_y_pos'][y])
        #         time.sleep(1.5)
        #         # A C T G
        #         # Choose Filter -> Open Shutter -> Imaging -> Close Shutter -> Save Image
        #         for i in range(1, 5):
        #             while self.state['ftblock_pos'] != i:
        #                 self._update_task_state(f'imaging: ({x},{y},{i})filter block -> {i}')
        #                 self.sig_mic_filter_block_move.emit(i)
        #                 time.sleep(1)
        #             self._update_task_state(f'imaging: ({x},{y},{i})filter block -> {i} open shutter {i}')
        #             self.sig_mic_shutter_open.emit(i)
        #             self.camera.startAcquisition()
        #             self._update_task_state(f'imaging: ({x},{y},{i})filter block -> {i} open shutter {i} ......')
        #             time.sleep(self.state['exposure_time'])
        #             while self.state['cam_state'] != 'IDLE':
        #                 pass
        #             self.sig_mic_close_all_shutter.emit()
        #             self._update_task_state(f'imaging: ({x},{y},{i}) acquire data')
        #             self.state['npimage'] = self.camera.camera.acquireData()
        #             self.camera.sig_image_data_ready.emit()
        #             time.sleep(1)
        #             self._update_task_state(f'imaging: ({x},{y},{i}) save image to file')
        #             tifffile.imsave(seq_state['current_seq_folder_name'] + '\\' + str(seq_state['current_cycle']) + f'\\pos_{x}_{y}_shutter{i}.tif', self.state['npimage'])
        # print('Done')

class seq_manager(QDialog):
    
    def __init__(self):
        super().__init__()
        self.state = state_singleton()
        loadUi('gui/seq_manager.ui', self)

        self._set_output_folder(os.getcwd() + '\\out')
        self.camera = camera()
        self.mic = microscope()
        self.flowcell = serial()
        self.stage = stage()

        self.seq_task = seq_task()

        self._set_current_state(seq_state['run_state'])
        self._set_current_task(seq_state['run_task'])

        self.seq_task.sig_update_run_state.connect(self.update_seq_state)
        self.seq_task.sig_update_task_state.connect(self.update_task_name)
        self.seq_task.sig_update_task_progress_bar.connect(self.update_task_progress_bar)

        self.seq_task.finished.connect(self.nextSeqCycle)

        self.outputFolderButton.clicked.connect(self.chooseDirctory)
        self.startSeqButton.clicked.connect(self.startSeq)
        self.abortButton.clicked.connect(self.abortSeq)

    @QtCore.pyqtSlot()
    def update_seq_state(self):
        self._set_current_state(seq_state['run_state'])

    @QtCore.pyqtSlot()
    def update_task_name(self):
        self._set_current_task(seq_state['run_task'])

    @QtCore.pyqtSlot(int, int)
    def update_task_progress_bar(self, cur, max):
        self._update_task_progress_bar(cur, max)

    @QtCore.pyqtSlot()
    def startSeq(self):
        seq_state['current_seq_folder_name'] = seq_state['output_folder'] + '\\' + datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs(seq_state['current_seq_folder_name'])
        self.seq_task.start()
        
    @QtCore.pyqtSlot()
    def abortSeq(self):
        self.seq_task.quit()
        seq_state['current_cycle'] = 0
        self._update_alltask_progress_bar(0, 0)
        self._update_task_progress_bar(0, 0)
        self._set_current_state('idle')
        self._set_current_task('no task')
        

    @QtCore.pyqtSlot()
    def nextSeqCycle(self):
        seq_state['current_cycle'] = seq_state['current_cycle'] + 1
        self._update_alltask_progress_bar(seq_state['current_cycle'], seq_state['total_cycle'])
        if seq_state['current_cycle'] == seq_state['total_cycle']:
            seq_state['current_cycle'] = 0
            self._set_current_state('finished')
            self._set_current_task('no task')
            return
        self.seq_task.start()
        
    @QtCore.pyqtSlot()
    def chooseDirctory(self):
        dir_choose = QFileDialog.getExistingDirectory(self, 'Choose output folder', seq_state['output_folder'])
        # seq_state['output_folder'] = dir_choose
        self._set_output_folder(dir_choose)

    def _set_output_folder(self, foldername):
        seq_state['output_folder'] = foldername
        self.outputfolder.setText(foldername)

    def _set_current_state(self, state_text):
        self.seqStateLabel.setText(state_text)

    def _set_current_task(self, task_name):
        self.currentTaskName.setText(task_name)

    def _update_alltask_progress_bar(self, cur, max):
        self.allTaskProgressBar.setValue(int(cur/max*100))

    def _update_task_progress_bar(self, cur, max):
        self.currentTaskProgressBar.setValue(int(cur/max*100))
    
    

