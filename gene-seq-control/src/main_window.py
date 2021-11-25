"""
Main Window

2021/11/10
"""


from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi

from .camera_window import camera_window
from .seq_manager import seq_manager
from .main_state import state_singleton

from .camera import camera
from .stage import stage
from .microscope import microscope

import logging
logger = logging.getLogger(__name__)

class main_window(QtWidgets.QMainWindow):
    """
    Main Window class
    """

    sig_set_emgain = QtCore.pyqtSignal(int)
    sig_set_coolertemperature = QtCore.pyqtSignal(int)
    sig_set_exposuretime = QtCore.pyqtSignal(float)

    sig_stage_moveabsolute = QtCore.pyqtSignal(float, float)
    sig_stage_xstep = QtCore.pyqtSignal(float)
    sig_stage_ystep = QtCore.pyqtSignal(float)
    sig_stage_enable = QtCore.pyqtSignal()
    sig_stage_disable = QtCore.pyqtSignal()

    sig_mic_tirf_insert = QtCore.pyqtSignal()
    sig_mic_tirf_extract = QtCore.pyqtSignal()
    sig_mic_tirf_step = QtCore.pyqtSignal(int)


    def __init__(self):
        super().__init__()

        loadUi('gui/main_view.ui', self)

        self.state = state_singleton()

        # Thread create
        self.camera_thread = QtCore.QThread()
        self.camera_worker = camera()
        self.camera_worker.moveToThread(self.camera_thread)
        self.camera_worker.sig_state_camera_update.connect(self.updateCameraState)

        self.stage_thread = QtCore.QThread()
        self.stage_worker = stage()
        self.stage_worker.moveToThread(self.stage_thread)
        self.stage_worker.sig_state_stage_update.connect(self.updateStageState)

        # self.mic_thread = QtCore.QThread()
        self.mic_worker = microscope()
        # self.mic_worker.moveToThread(self.mic_thread)
        self.mic_worker.sig_state_microscope_update.connect(self.updateMicState)

        # Create windows
        self.camera_window = camera_window()
        self.camera_window.show()

        self.seq_manager = seq_manager()
        self.seq_manager.show()
        
        # Thread up
        self.camera_thread.start()
        self.stage_thread.start()
        # self.mic_thread.start()

        self.state.sig_update_request.connect(self.camera_worker.updateCameraState)
        self.state.sig_update_request.connect(self.stage_worker.updateStageState)
        self.state.sig_update_request.connect(self.mic_worker.updateMicroscopeState)

        # Microscope signal
        self.tirfToggleButton.clicked.connect(self.handleTirfInsertButton)
        self.sig_mic_tirf_insert.connect(self.mic_worker.insertTirf)
        self.sig_mic_tirf_extract.connect(self.mic_worker.extractTirf)
        self.addTirfPosButton.clicked.connect(self.tirfPosUp)
        self.minusTirfPosButton.clicked.connect(self.tirfPosDown)
        self.sig_mic_tirf_step.connect(self.mic_worker.tirfStep)

        # Stage signal
        self.enableStageButton.clicked.connect(self.handleEnable)
        self.sig_stage_enable.connect(self.stage_worker.enable)
        self.sig_stage_disable.connect(self.stage_worker.disable)
        self.homeStageButton.clicked.connect(self.stage_worker.home)
        self.stageGoButton.clicked.connect(self.stageMoveAbsolute)
        self.sig_stage_moveabsolute.connect(self.stage_worker.moveAbsolute)
        self.xPosPlusButton.clicked.connect(self.stageXStepUp)
        self.xPosMinusButton.clicked.connect(self.stageXStepDown)
        self.yPosPlusButton.clicked.connect(self.stageYStepUp)
        self.yPosMinusButton.clicked.connect(self.stageYStepDown)
        self.sig_stage_xstep.connect(self.stage_worker.stepX)
        self.sig_stage_ystep.connect(self.stage_worker.stepY)

        # Camera signal
        self.setExposureTimeButton.clicked.connect(self.setExposureTime)
        self.sig_set_exposuretime.connect(self.camera_worker.setExposureTime)
        self.setTemperatureButton.clicked.connect(self.setCoolerTemperature)
        self.sig_set_coolertemperature.connect(self.camera_worker.setTemperature)
        self.coolerONButton.clicked.connect(self.camera_worker.coolerON)
        self.coolerOFFButton.clicked.connect(self.camera_worker.coolerOFF)
        self.fanHighButton.clicked.connect(self.camera_worker.fanHigh)
        self.fanLowButton.clicked.connect(self.camera_worker.fanLow)
        self.fanOFFButton.clicked.connect(self.camera_worker.fanOff)
        self.setEMGainButton.clicked.connect(self.setEMGain)
        self.sig_set_emgain.connect(self.camera_worker.setEMGain)

        self.camera_worker.notify_all_state()
        self.stage_worker.notify_all_state()
        self.mic_worker.notify_all_state()
        
    def __del__(self):
        try:
            self.camera_thread.quit()
            self.stage_thread.quit()
            # self.mic_thread.quit()

            self.camera_thread.wait()
            self.stage_thread.wait()
            # self.mic_thread.wait()
        except:
            pass

    @QtCore.pyqtSlot()
    def handleEnable(self):
        if self.state['enabled']:
            self.enableStageButton.setText('Enable')
            self.sig_stage_disable.emit()
        else:
            self.enableStageButton.setText('Disable')
            self.sig_stage_enable.emit()

    @QtCore.pyqtSlot()
    def setEMGain(self):
        logger.info('Set EM Gain')
        gain = int(self.emGainLineEdit.text())
        self.sig_set_emgain.emit(gain)

    @QtCore.pyqtSlot()
    def setCoolerTemperature(self):
        logger.info('Set Cooler Temperature')
        temp = int(self.cameraTemperatureLineEdit.text())
        self.sig_set_coolertemperature.emit(temp)

    @QtCore.pyqtSlot()
    def setExposureTime(self):
        logger.info('Set exposure time')
        sec = float(self.exposureTimeLineEdit.text())
        self.sig_set_exposuretime.emit(sec)

    @QtCore.pyqtSlot()
    def tirfPosUp(self):
        logger.info('Tirf Pos up')
        step = int(self.tirfStepLineEdit.text())
        self.sig_mic_tirf_step.emit(step)

    @QtCore.pyqtSlot()
    def tirfPosDown(self):
        logger.info('Tirf Pos donw')
        step = int(self.tirfStepLineEdit.text())
        self.sig_mic_tirf_step.emit(-1 * step)

    @QtCore.pyqtSlot()
    def stageMoveAbsolute(self):
        logger.info('Stage Move absolute')
        x = float(self.xPosInputLabel.text())
        y = float(self.yPosInputLabel.text())
        self.sig_stage_moveabsolute.emit(x, y)

    @QtCore.pyqtSlot()
    def stageXStepUp(self):
        logger.info('Stage x step up')
        step = float(self.stepInputLabel.text())
        self.sig_stage_xstep.emit(step)

    @QtCore.pyqtSlot()
    def stageXStepDown(self):
        logger.info('Stage x step down')
        step = float(self.stepInputLabel.text())
        self.sig_stage_xstep.emit(-1 * step)

    @QtCore.pyqtSlot()
    def stageYStepUp(self):
        logger.info('Stage y step up')
        step = float(self.stepInputLabel.text())
        self.sig_stage_ystep.emit(step)

    @QtCore.pyqtSlot()
    def stageYStepDown(self):
        logger.info('Stage y step down')
        step = float(self.stepInputLabel.text())
        self.sig_stage_ystep.emit(-1 * step)

    @QtCore.pyqtSlot()
    def handleTirfInsertButton(self):
        if self.state['tirf_inserted']:
            self.sig_mic_tirf_extract.emit()
        else:
            self.sig_mic_tirf_insert.emit()


    @QtCore.pyqtSlot(str)
    def updateCameraState(self, k):
        if k == 'exposure_time':
            self.exposureTimeLabel.setText(str(round(self.state['exposure_time'], 5)) + ' s')
        if k == 'cam_temperature':
            self.cameraTemperatureLabel.setText(str(round(self.state['cam_temperature'], 2)))
        if k == 'cam_cooler_state':
            self.cameraCoolerState.setText(self.state['cam_cooler_state'])
        if k == 'em_gain':
            self.emGainLabel.setText(str(self.state['em_gain']))

    @QtCore.pyqtSlot(str)
    def updateStageState(self, k):
        if k == 'x_pos':
            self.xdrivePosLabel.setText(str(self.stage_worker.xpos_to_mm(self.state['x_pos'])) + ' mm')
        if k == 'y_pos':
            self.ydrivePosLabel.setText(str(self.stage_worker.ypos_to_mm(self.state['y_pos'])) + ' mm')
        if k == 'homed':
            self.homeDisplayLabel.setText('Homed' if self.state['homed'] else 'Not Homed')
        if k == 'enabled':
            self.enableDisplayLabel.setText('Enabled' if self.state['enabled'] else 'Not Enable')
    
    @QtCore.pyqtSlot(str)
    def updateMicState(self, k):
        if k == 'z_pos':
            self.zdrivePosLabel.setText(str(self.mic_worker.zpos_to_um(self.state['z_pos'])) + ' um')
        if k == 'pfs_pos':
            self.pfsPosLabel.setText(str(self.state['pfs_pos']))
        if k == 'tirf_pos':
            self.tirfPosLabel.setText(str(self.state['tirf_pos']))
        if k == 'tirf_inserted':
            self.tirfStateLabel.setText('Insert' if self.state['tirf_inserted'] else 'Not Insert')