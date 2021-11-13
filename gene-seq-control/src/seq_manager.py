"""
Seq Manager Window
  2021/11/13

"""

import os

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from .main_state import state_singleton

import logging
logger = logging.getLogger(__name__)


class seq_manager(QDialog):
    
    def __init__(self):
        super().__init__()
        self.state = state_singleton()
        loadUi('gui/seq_manager.ui', self)

        self.output_folder = os.getcwd() + '/out'
        print(self.output_folder)

        print('init')
