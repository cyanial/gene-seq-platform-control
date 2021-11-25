"""
Seq Manager Window
  2021/11/13

"""

import os

import PyQt5.QtCore

from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi

from .main_state import state_singleton

import logging
logger = logging.getLogger(__name__)


class seq_manager(QDialog):
    
    def __init__(self):
        super().__init__()
        self.state = state_singleton()
        loadUi('gui/seq_manager.ui', self)

        self._set_output_folder(os.getcwd() + '\\out')

        self.outputFolderButton.clicked.connect(self.chooseDirctory)

    @PyQt5.QtCore.pyqtSlot()
    def chooseDirctory(self):
        dir_choose = QFileDialog.getExistingDirectory(self, 'Choose output folder', self.output_folder)
        self._set_output_folder(dir_choose)

    def _set_output_folder(self, foldername):
        self.output_folder = foldername
        self.outputfolder.setText(foldername)
