

import sys

import logging
import time

from PyQt5 import QtWidgets

from src.main_window import main_window




timestr = time.strftime("%Y%m%d-%H%M%S")
logging_filename = timestr + '.log'
logging.basicConfig(filename='log/' + logging_filename,
        level=logging.INFO, 
        format='%(asctime)s-%(levelname)s-%(name)s-%(message)s')
logger = logging.getLogger(__name__)
logger.info('app start')


def start():
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = main_window()
    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start()