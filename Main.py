import sys
import os
import time
import threading

try:
	from PySide.QtGui import *
	from PySide.QtCore import *
except:
	os.system("C:\\Python\\Scripts\\pip.exe install PySide")
	raw_input("\n\nRestart Program!")
	sys.exit()

from Backend import Backend
from SoundMixer import SoundMixer
from Widgets import *

class MainWindow(QWidget):
	WIDTH   = 900
	HEIGHT  = WIDTH/12*8

	change_color = Signal(str)
	make_window  = Signal(tuple)

	def __init__(self):
		QWidget.__init__(self)
		self.initUI()
		self.create_colors()
		self.draw_bg(self.current_color)
		self.create_widgets()
		self.create_backend()

		self.bind_signals()
		self.create_sounds()
		#self.backend.get_random_item('armor')

	def initUI(self):
		self.resize(self.WIDTH, self.HEIGHT)
		self.setFixedSize(QSize(self.WIDTH,self.HEIGHT))
		self.setWindowTitle("Happy Cards Simulator")

		with open('stylesheet.css','r') as f:
			self.setStyleSheet(f.read())

	def create_widgets(self):
		self.tickets = 500
		self.is_loading = False
		self._tickets = Tickets(str(self.tickets), self)
		self._tickets.move(520,50)

		red = ItemCliker("",self,"red","weapon")
		red.move(115, 140)
		red.clicked.connect(self.generate_card)

		yellow = ItemCliker("",self,"yellow","shield")
		yellow.move(235, 210)
		yellow.clicked.connect(self.generate_card)

		purple = ItemCliker("",self,"purple","armor")
		purple.move(100, 285)
		purple.clicked.connect(self.generate_card)

		green = ItemCliker("",self,"green","helmet")
		green.move(200, 375)
		green.clicked.connect(self.generate_card)

		blue = ItemCliker("",self,"blue","acc")
		blue.move(120, 470)
		blue.clicked.connect(self.generate_card)

		# create star fragments
		self.frags = []
		self.star_amount = 0

		for i in range(12): #405
			mv = 30 * i + 405
			star_frag = StarFragment('',self)
			star_frag.turn_off.emit()
			star_frag.move(mv,484)
			self.frags.append(star_frag)

	def generate_card(self, color):
		if color == 'red': itemtype = "weapon"
		elif color == 'yellow': itemtype = "shield"
		elif color == 'green': itemtype = "helmet"
		elif color == 'blue': itemtype = "acc"
		elif color == 'purple': itemtype = "armor"
		else: itemtype = "weapon"

		if not self.is_loading:
			if self.tickets <= 17:
				MessageBox().showinfo("Ticket Error","Not Enough Happy Tickets left!")
				return
			else:
				self.tickets -= 18
				self._tickets.setText(str(self.tickets))

			self.create_thread(self.create_happy_card, itemtype)

	def create_happy_card(self, itemtype):
		self.is_loading = True

		# make sounds
		self.mixer.card_start.play(1)
		time.sleep(0.2)
		self.mixer.sizzle.play(1)
		time.sleep(3)
		self.mixer.card_start.stop()
		self.mixer.sizzle.stop()
		self.mixer.card_open.play(1)
		self.make_window.emit(itemtype)
		self.mixer.card_open.stop()

	def create_window(self, itemtype):
		# Use the random card info
		if self.star_amount >= 12:
			force_sp = True
		else:
			force_sp = False
		items, is_sp = self.backend.get_random_item(itemtype, force_sp)
		if force_sp: is_sp = True

		new_window = HappyCardsWindow((items, is_sp), itemtype, self)
		new_window.exec_()
		self.is_loading = False

		# add star fragments
		if self.star_amount >= 12:
			self.star_amount = 0
			self.load_frags()
			return

		if self.backend.random_success(10)[0]:
			self.star_amount += 5
			self.load_frags()
			return

		if self.backend.random_success(30)[0]:
			self.star_amount += 4
			self.load_frags()
			return

		if self.backend.random_success(40)[0]:
			self.star_amount += 3
			self.load_frags()
			return

		if self.backend.random_success(60)[0]:
			self.star_amount += 2
		else:
			self.star_amount += 1
		self.load_frags()

	def load_frags(self):
		on = range(self.star_amount)
		for x in self.frags:
			place = self.frags.index(x)
			if place in on:
				x.turn_on.emit()
			else:
				x.turn_off.emit()

	def bind_signals(self):
		self.change_color.connect(self.draw_bg)
		self.make_window.connect(self.create_window)

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

	def create_sounds(self):
		self.mixer = SoundMixer(self)
		self.mixer.bg.set_volume(0.6)
		self.mixer.bg.play(-1)

	def create_thread(self, func, *args):
		t = threading.Thread(target=func,args=args)
		t.daemon = True
		t.start()

if __name__ == '__main__':
	app = QApplication(sys.argv)

	win = MainWindow()
	win.show()

	sys.exit(app.exec_())