from PySide.QtGui import *
from PySide.QtCore import *

import sys
import os

from Backend import Backend

class MainWindow(QWidget):
	WIDTH   = 640
	HEIGHT  = WIDTH/12*9

	def __init__(self):
		QWidget.__init__(self)
		self.initUI()
		self.create_backend()

	def initUI(self):
		self.resize(self.WIDTH, self.HEIGHT)
		self.setWindowTitle("Happy Cards Simulator")

	def create_backend(self):
		self.backend = Backend()

if __name__ == '__main__':
	app = QApplication(sys.argv)

	win = MainWindow()
	win.show()

	sys.exit(app.exec_())