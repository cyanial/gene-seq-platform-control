"""
Main Window

2021/11/10
"""


from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi

from .camera_window import camera_window
from .main_state import state_singleton

import logging
logger = logging.getLogger(__name__)

class main_window(QtWidgets.QMainWindow):
    """
    Main Window class
    """

    def __init__(self):
        super().__init__()

        loadUi('gui/mainview.ui', self)

        self.state = state_singleton()

        self.camera_window = camera_window()
        self.camera_window.show()

        self.state.sig_state_updated.connect(self.updateGui)

        self.enableStageButton.clicked.connect(self.handleButtonEnable)
        self.homeStageButton.clicked.connect(self.homeStage)
        self.tirfToggleButton.clicked.connect(self.handleTirfInsertButton)
        self.stageGoButton.clicked.connect(self.stageMoveAbsolute)
        self.xPosPlusButton.clicked.connect(self.stageXStepUp)
        self.xPosMinusButton.clicked.connect(self.stageXStepDown)
        self.yPosPlusButton.clicked.connect(self.stageYStepUp)
        self.yPosMinusButton.clicked.connect(self.stageYStepDown)
        self.addTirfPosButton.clicked.connect(self.tirfPosUp)
        self.minusTirfPosButton.clicked.connect(self.tirfPosDown)
        
    def enableStage(self):
        logger.info('Enable Stage')
        self.state.getStage().enable()

    def disableStage(self):
        logger.info('Disable Stage')
        self.state.getStage().disable()

    @QtCore.pyqtSlot()
    def tirfPosUp(self):
        logger.info('Tirf Pos up')
        step = int(self.tirfStepLineEdit.text())
        self.state.getMicroscope().tirfMoveRealtive(step)

    @QtCore.pyqtSlot()
    def tirfPosDown(self):
        logger.info('Tirf Pos donw')
        step = int(self.tirfStepLineEdit.text())
        self.state.getMicroscope().tirfMoveRealtive(-1 * step)

    @QtCore.pyqtSlot()
    def stageMoveAbsolute(self):
        logger.info('Stage Move absolute')
        x = float(self.xPosInputLabel.text())
        y = float(self.yPosInputLabel.text())
        self.state.getStage().moveAbs_mm(x, y)

    @QtCore.pyqtSlot()
    def stageXStepUp(self):
        logger.info('Stage x step up')
        step = float(self.stepInputLabel.text())
        self.state.getStage().moveXRel_mm(step)

    @QtCore.pyqtSlot()
    def stageXStepDown(self):
        logger.info('Stage x step down')
        step = float(self.stepInputLabel.text())
        self.state.getStage().moveXRel_mm(-1 * step)

    @QtCore.pyqtSlot()
    def stageYStepUp(self):
        logger.info('Stage y step up')
        step = float(self.stepInputLabel.text())
        self.state.getStage().moveYRel_mm(step)

    @QtCore.pyqtSlot()
    def stageYStepDown(self):
        logger.info('Stage y step down')
        step = float(self.stepInputLabel.text())
        self.state.getStage().moveXRel_mm(-1 * step)

    @QtCore.pyqtSlot()
    def homeStage(self):
        logger.info('Homing Stage')
        self.state.getStage().home()

    @QtCore.pyqtSlot()
    def handleButtonEnable(self):
        if self.state.isEnabled():
            self.disableStage()
        else:
            self.enableStage()

    @QtCore.pyqtSlot()
    def handleTirfInsertButton(self):
        if self.state.tirfInserted():
            self.state.getMicroscope().tirfExtract()
        else:
            self.state.getMicroscope().tirfInsert()


    @QtCore.pyqtSlot(str)
    def updateGui(self, item):
        if item == 'z_pos':
            self.zdrivePosLabel.setText(str(self.state.zpos_to_um()) + ' um')
        if item == 'x_pos':
            self.xdrivePosLabel.setText(str(self.state.xpos_to_mm()) + ' mm')
        if item == 'y_pos':
            self.ydrivePosLabel.setText(str(self.state.ypos_to_mm()) + ' mm')
        if item == 'pfs_pos':
            self.pfsPosLabel.setText(str(self.state.pfsPos()))
        if item == 'tirf_pos':
            self.tirfPosLabel.setText(str(self.state.tirfPos()))
        if item == 'homed':
            self.homeDisplayLabel.setText('Homed' if self.state.isHomed() else 'Not Home')
        if item == 'enabled':
            if self.state.isEnabled():
                self.enableStageButton.setText('Disable')
                self.enableDisplayLabel.setText('Enabled')
            else:
                self.enableStageButton.setText('Enable')
                self.enableDisplayLabel.setText('Not Enable')
        if item == 'tirf_inserted':
            if self.state.tirfInserted():
                self.tirfToggleButton.setText('Extract')
                self.tirfStateLabel.setText('Inserted')
            else:
                self.tirfToggleButton.setText('Insert')
                self.tirfStateLabel.setText('Not Insert')