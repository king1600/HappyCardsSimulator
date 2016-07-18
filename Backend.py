import os
import json
import random
import threading

from Buffs import BUFFS

class Backend(object):
	CACHE_FILE = "cache.json"

	classes  = ["warrior","cleric","mage"]

	is_spremium   = False
	is_high_buff  = False
	is_super      = False
	is_istense    = False
	chances	   = {
		'sp_on_happy_time':14,
		'high_buff':	   60,
		'strong':          10,
		'intense':         5
	}

	def __init__(self):
		self.load_cache()
		self.pick_random_type()

	def load_cache(self):
		with open(self.CACHE_FILE, 'r') as f:
			self.data = json.loads( f.read() )

		self.get_random_item("weapon")

	def get_random_item(self, itemtype):
		# item_entry =  (item name, item info, random buff)
		# return 3 item entries (normal, normal, prem or sp)
		status = self.pick_random_type()
		print "is sp: "+repr(status[1])

		ITEMS = []

		for x in [1,2,3]:

			# generate item choices based on weight
			item_choices = self.data[status[0]][itemtype]
			_choices = list([ z for z in item_choices ])
			good = {}

			for y in _choices:
				data = item_choices[y]

				# normal premiums
				if x in [1,2]:
					mx_w = self.correct_weight(itemtype, False) - 1
					if data['weight'] <= mx_w:
						good[y] = data

				# super premiums
				else:
					mx_w = self.correct_weight(itemtype, status[1])
					if status[1]:
						if data['weight'] >= mx_w and data['weight'] <= 10:
							good[y] = data
					else:
						if data['weight'] == mx_w:
							good[y] = data

			# get random item from choices
			available = [ a for a in good ]
			random.shuffle( available )
			item_name = random.choice(available)

			# add to items to display
			ITEMS.append( [item_name, good[item_name], None])

		for x in ITEMS:
			print x[0], x[1]['weight']

		return ITEMS

	def correct_weight(self, itemtype, is_sp):
		if itemtype == "weapon":
			if is_sp: lowest_weight = 9
			else: lowest_weight = 7
		elif itemtype == "shield":
			if is_sp: lowest_weight = 5
			else: lowest_weight = 4
		elif itemtype == "armor":
			if is_sp: lowest_weight = 9
			else: lowest_weight = 7
		elif itemtype == "helmet":
			if is_sp: lowest_weight = 9
			else: lowest_weight = 6
		else:
			if is_sp: lowest_weight = 5
			else: lowest_weight = 4
		return lowest_weight

	def pick_random_type(self):
		# returns tuple (class, is_sp, is_high, is_strong, is_intense)

		random.shuffle(self.classes)
		r_class = random.choice(self.classes)

		# is it super_premium?
		self.is_spremium = False
		r_sp_chances = self.random_success(self.chances['sp_on_happy_time'])
		if r_sp_chances[0]: self.is_spremium = True

		# does it have high buff?
		self.is_high_buff = False
		r_sp_chances = self.random_success(self.chances['high_buff'])
		if r_sp_chances[0]: self.is_high_buff = True


		self.is_super = False
		r_sp_chances = self.random_success(self.chances['strong'])
		if r_sp_chances[0]: self.is_super = True

		self.is_istense = False
		r_sp_chances = self.random_success(self.chances['intense'])
		if r_sp_chances[0]: self.is_istense = True

		return (r_class, self.is_spremium, self.is_high_buff, self.is_super, self.is_istense)

	def random_success(self, chance):
		nums = range(0,101)
		random.shuffle(nums)
		choices = []
		random_choice = random.choice(nums)

		for x in range(chance):
			c = nums.pop(nums.index(random.choice(nums)))
			choices.append( c )

		if random_choice in choices:
			return (True, random_choice) # It succeded being in chance!
		else:
			return (False, random_choice) # failed