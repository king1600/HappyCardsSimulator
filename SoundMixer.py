from pygame import mixer
import os

class SoundMixer(object):

	SOUND_PATHS = {
		'bg':os.path.join("sounds","idle_music.ogg"),
		'normal_item':os.path.join("sounds","non_sp.ogg"),
		'premium':os.path.join("sounds","premium.ogg"),
		'super_premium':os.path.join("sounds","sp_sound.ogg"),

		'card_start':os.path.join("sounds","start.ogg"),
		'sizzle':os.path.join("sounds","waiting.ogg"),
		'card_open':os.path.join("sounds","pop.ogg")
	}

	def __init__(self, window):
		mixer.init()

		self.bg = mixer.Sound( self.SOUND_PATHS['bg'] )
		self.normal_item = mixer.Sound( self.SOUND_PATHS['normal_item'] )
		self.premium = mixer.Sound( self.SOUND_PATHS['premium'] )
		self.super_premium = mixer.Sound( self.SOUND_PATHS['super_premium'] )

		self.card_start = mixer.Sound( self.SOUND_PATHS['card_start'] )
		self.sizzle = mixer.Sound( self.SOUND_PATHS['sizzle'] )
		self.card_open = mixer.Sound( self.SOUND_PATHS['card_open'] )

		self.all_sounds = [self.normal_item,self.premium,
			self.super_premium,self.card_start,self.sizzle,self.card_open]

		for s in self.all_sounds:
			s.set_volume(0.6)

