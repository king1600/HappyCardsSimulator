import os
import json

from Buffs import BUFFS

class Backend(object):
	CACHE_FILE = "cache.json"

	def __init__(self):
		self.load_cache()

	def load_cache(self):
		with open(self.CACHE_FILE, 'r') as f:
			self.data = json.loads( f.read() )