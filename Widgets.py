from PySide.QtGui import *
from PySide.QtCore import *

import os
import threading
import urllib2

class ItemFrame(QFrame):
	set_img_data = Signal(tuple)

	def __init__(self, info, itemtype, window, is_sp=False):
		QFrame.__init__(self)
		self.window = window
		self.item_info = info[1]
		self.rand_buff = info[2]
		self.item_name = info[0]
		self.is_sp = is_sp

		self.itemtype = itemtype

		self.layout = QVBoxLayout()
		self.layout.setSpacing(10)
		self.setLayout(self.layout)

		self.create_widgets()
		self.set_img_data.connect(self.set_data)
		self.layout.addStretch(1)

		with open('stylesheet.css','r') as f:
			self.setStyleSheet(f.read())

		if self.is_sp:
			self.setStyleSheet("""QFrame {
					background-color: #FBC242
				}
				QLabel { color: black; }""")

	def create_widgets(self):

		self.item_image = QLabel()
		self.item_image.setAlignment(Qt.AlignCenter)

		self.i_name = QLabel(u"{}".format(self.item_name))
		self.i_name.setAlignment(Qt.AlignCenter)

		self.layout.addWidget(self.i_name)
		self.layout.addWidget(self.item_image)

		self.layout.addWidget(HLine())
		layout = QGridLayout()

		# stats
		if self.itemtype == 'weapon':
			layout.addWidget(QLabel("Attack:"), 0, 0)
			layout.addWidget(QLabel(str(self.item_info['Attack'])), 0, 1)

			layout.addWidget(QLabel("Magic Attack:"), 1, 0)
			layout.addWidget(QLabel(str(self.item_info['Magic Attack'])), 1, 1)

		elif self.itemtype in ['armor','helmet']:
			layout.addWidget(QLabel("Defense:"), 0, 0)
			layout.addWidget(QLabel(str(self.item_info['Defense'])), 0, 1)

			layout.addWidget(QLabel("Magic Defense:"), 1, 0)
			layout.addWidget(QLabel(str(self.item_info['Magic Defense'])), 1, 1)

		elif self.itemtype == 'shield':
			layout.addWidget(QLabel("Guard power:"), 0, 0)
			layout.addWidget(QLabel(str(self.item_info['Guard power'])), 0, 1)

			layout.addWidget(QLabel("Magic guard:"), 1, 0)
			layout.addWidget(QLabel(str(self.item_info['Magic guard'])), 1, 1)

		else:
			pass
		self.layout.addLayout(layout)
		self.layout.addWidget(HLine())

		# buffs
		slots = int(self.item_info['slots']) - 1 #random buff
		slot_layout = QVBoxLayout()
		slot_layout.setSpacing(20)

		# permanent buffs
		for x in self.item_info['buffs']:
			l = QLabel(u"{}".format(x))
			l.setAlignment(Qt.AlignCenter)
			slot_layout.addWidget(l)
			slots -= 1

		# random buff
		l = QLabel(u"{}".format(self.rand_buff))
		l.setAlignment(Qt.AlignCenter)
		slot_layout.addWidget(l)

		# empty slots
		if slots > 0:
			for x in range(slots):
				l = QLabel(u"{}".format("[ Empty Slot ]"))
				l.setAlignment(Qt.AlignCenter)
				slot_layout.addWidget(l)

		self.layout.addLayout(slot_layout)

		# load image data
		self.create_thread(self.load_url_data)

	def set_data(self, imgdata):
		i = QImage()
		i.loadFromData(imgdata)
		pixmap = QPixmap(i).scaled(128,128, Qt.KeepAspectRatio)
		self.item_image.setPixmap(pixmap)

	def load_url_data(self):
		url = self.item_info['image']
		data = urllib2.urlopen(url).read()
		self.set_img_data.emit((data))

	def create_thread(self, func, *args):
		t = threading.Thread(target=func,args=args)
		t.daemon = True
		t.start()


class HappyCardsWindow(QDialog):
	def __init__(self, info, itemtype, parent=None):
		self.win = parent
		self.items, self.is_sp = info
		self.itemtype = itemtype

		super(HappyCardsWindow, self).__init__(parent=parent)
		self.initUI()

	def initUI(self):
		self.resize( 360, 360 )
		self.setWindowTitle("Card Opening")

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.create_widgets()

	def create_widgets(self):
		# lower bg music
		mixer = self.win.mixer

		mixer.bg.set_volume(0.4)

		self.sounds = [mixer.normal_item, mixer.normal_item]
		if self.is_sp: self.sounds.append(mixer.super_premium)
		else: self.sounds.append(mixer.premium)

		self.frames = []
		for x in self.items:
			if x == self.items[-1] and self.is_sp:
				item_frame = ItemFrame(x, self.itemtype, self.win, True)
			else:
				item_frame = ItemFrame(x, self.itemtype, self.win)
			self.layout.addWidget(item_frame)
			self.frames.append(item_frame)

		self.frame_count = -1
		self.last_sound = None
		self.show_next_frame()

	def mousePressEvent(self, event):
		self.show_next_frame()

	def show_next_frame(self):
		# calculate next frame
		self.frame_count += 1
		if self.frame_count > 2:
			self.win.mixer.bg.set_volume(0.6)
			self.close()
			return

		# play sound
		try:
			self.last_sound.stop()
		except:
			pass
		self.last_sound = self.sounds[self.frame_count]
		self.last_sound.play()

		# show frame
		my_frame = self.frames[self.frame_count]
		for x in self.frames:
			if x == my_frame: x.show()
			else: x.hide()

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

class HLine(QFrame):
	def __init__(self):
		QFrame.__init__(self)
		self.setFrameStyle(QFrame.HLine)
		self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)

class MessageBox:
	def __init__(self):
		self.msg = QMessageBox()

	def showinfo(self, title, text):
		self.showMessage(title, text, QMessageBox.Information)

	def showwarning(self, title, text):
		self.showMessage(title, text, QMessageBox.Warning)

	def showerror(self, title, text):
		self.showMessage(title, text, QMessageBox.Critical)

	def showMessage(self, title, text, icon):
		self.msg.setIcon(icon)
		self.msg.setWindowTitle(title)
		self.msg.setText(unicode(text))
		self.msg.exec_()