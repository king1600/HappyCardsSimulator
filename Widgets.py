from PySide.QtGui import *
from PySide.QtCore import *

import os
import threading
import urllib2

class ItemCliker(QLabel):
	clicked = Signal(str)

	WIDTH = 64
	HEIGHT = 78
	SIZE = (WIDTH, HEIGHT)

	def __init__(self, text='', parent=None, color='', itemtype=''):
		self.color = color
		self.itemtype = itemtype
		self.win = parent
		QLabel.__init__(self, text, parent=parent)

		
		self.resize(self.WIDTH,self.HEIGHT)
		self.setMinimumHeight(self.HEIGHT)
		self.setMinimumWidth(self.WIDTH)

		#self.setStyleSheet("background-color: "+color+";")

	def enterEvent(self, event):
		if self.win.current_color != self.color:
			self.win.change_color.emit(self.color)
			self.win.current_color = self.color

	def mousePressEvent(self, event):
		self.clicked.emit(self.color)

class StarFragment(QLabel):
	turn_on  = Signal()
	turn_off = Signal()

	def __init__(self,text='',parent=None):
		self.win = parent
		QLabel.__init__(self, text, parent=parent)

		self.on = QPixmap(os.path.join("images","on_star.png"))
		self.on = self.on.scaled(37, 40, Qt.KeepAspectRatio)

		self.off = QPixmap(os.path.join("images","off_star.png"))
		self.off = self.off.scaled(37, 40, Qt.KeepAspectRatio)

		self.turn_on.connect(self.set_on)
		self.turn_off.connect(self.set_off)

		self.turn_on.emit()

	def set_on(self):
		self.setPixmap(self.on)

	def set_off(self):
		self.setPixmap(self.off)

class Tickets(QLabel):
	def __init__(self, text='', parent=None):
		self.win = parent
		QLabel.__init__(self, text, parent=parent)
		self.setAlignment(Qt.AlignRight)
