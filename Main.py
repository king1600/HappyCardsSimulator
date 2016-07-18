from PySide.QtGui import *
from PySide.QtCore import *

import sys
import os

from Backend import Backend
from Widgets import *

class MainWindow(QWidget):
	WIDTH   = 900
	HEIGHT  = WIDTH/12*8

	change_color = Signal(str)

	def __init__(self):
		QWidget.__init__(self)
		self.initUI()
		self.create_colors()
		self.draw_bg(self.current_color)
		self.create_widgets()
		#self.create_backend()

		self.bind_signals()

	def initUI(self):
		self.resize(self.WIDTH, self.HEIGHT)
		self.setFixedSize(QSize(self.WIDTH,self.HEIGHT))
		self.setWindowTitle("Happy Cards Simulator")

	def create_widgets(self):
		red = ItemCliker("",self,"red","weapon")
		red.move(115, 140)

		yellow = ItemCliker("",self,"yellow","shield")
		yellow.move(235, 210)

		purple = ItemCliker("",self,"purple","armor")
		purple.move(100, 285)

		green = ItemCliker("",self,"green","helmet")
		green.move(200, 375)

		blue = ItemCliker("",self,"blue","acc")
		blue.move(120, 470)

	def bind_signals(self):
		self.change_color.connect(self.draw_bg)

	def create_colors(self):
		self.color_bgs = {
			'red':QPixmap(os.path.join('images','red.png')).scaled(self.WIDTH, self.HEIGHT),
			'yellow':QPixmap(os.path.join('images','yellow.png')).scaled(self.WIDTH, self.HEIGHT),
			'green':QPixmap(os.path.join('images','green.png')).scaled(self.WIDTH, self.HEIGHT),
			'blue':QPixmap(os.path.join('images','blue.png')).scaled(self.WIDTH, self.HEIGHT),
			'purple':QPixmap(os.path.join('images','purple.png')).scaled(self.WIDTH, self.HEIGHT)
		}
		self.current_color = 'red'

	def draw_bg(self, color):
		pixmap = self.color_bgs[str(color)]
		palette = QPalette()
		palette.setBrush(QPalette.Background,QBrush(pixmap))
		self.setPalette(palette)

	def create_backend(self):
		self.backend = Backend()

if __name__ == '__main__':
	app = QApplication(sys.argv)

	win = MainWindow()
	win.show()

	sys.exit(app.exec_())