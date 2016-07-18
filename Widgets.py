from PySide.QtGui import *
from PySide.QtCore import *

import os
import threading
import urllib2

class ItemCliker(QLabel):
	clicked = Signal()
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