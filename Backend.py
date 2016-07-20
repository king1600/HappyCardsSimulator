import os
import json
import random
import copy
import threading

from Buffs import BUFFS

class Backend(object):
	CACHE_FILE = "cache.json"

	classes  = ["warrior","cleric","mage"]
	strongs  = ['aid','slayer','Anti-Guard']
	intenses = ['intens','far','reach','super','fast','longer']
	goods    = ['3','effect','weight','crush','dash attack']

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
		self.buffs = BUFFS
		self.load_cache()
		#self.pick_random_type()

	def load_cache(self):
		with open(self.CACHE_FILE, 'r') as f:
			self.data = json.loads( f.read() )

		#self.get_random_item("weapon")

	def get_random_item(self, itemtype, force_sp=False):
		# item_entry =  (item name, item info, random buff)
		# return 3 item entries (normal, normal, prem or sp)
		status = self.pick_random_type()

		ITEMS = []

		for x in [1,2,3]:

			# generate item choices based on weight
			if itemtype in ['shield','acc']:
				item_choices = self.data[itemtype]
			else:
				item_choices = self.data[status[0]][itemtype]
			_choices = list([ z for z in item_choices ])
			good = {}
			is_sp = False

			for y in _choices:
				data = item_choices[y]

				# normal premiums
				if x in [1,2]:
					mx_w = self.correct_weight(itemtype, False) - 1
					if data['weight'] <= mx_w:
						good[y] = data

				# super premiums
				else:
					is_sp = True
					mx_w = self.correct_weight(itemtype, status[1])
					if status[1] or force_sp:
						if data['weight'] >= mx_w and data['weight'] <= 10:
							good[y] = data
					else:
						if data['weight'] == mx_w:
							good[y] = data

			# get random item from choices
			available = [ a for a in good ]
			random.shuffle( available )
			item_name = random.choice(available)

			rand_buff = self.get_random_buff(itemtype, status, good[item_name], is_sp)

			# add to items to display
			ITEMS.append( [item_name, good[item_name], rand_buff])

		#for x in ITEMS:
		#	print x[0], x[-1]

		return (ITEMS, status[1])

	def get_random_buff(self, itemtype, status, info, is_sp):

		# generate choices
		if itemtype not in ['shield','acc']: choices = self.buffs[itemtype]['all']
		else: choices = self.buffs[itemtype]

		# randomize buff choices
		random.shuffle(choices)

		### Case Armor, weapon, or helmet
		if itemtype in ['armor','weapon','helmet']:
			good = [] # list of possible choices after filter

			# check if its premium or super premium
			if is_sp:
				# intensify buff
				if status[4]:
					return self.check_if_already(good, info, choices)

				# slayer worthy
				if status[3]:
					good = self.remove_type(choices, self.intenses) # remove intense buffs
					return self.check_if_already(good, info, choices)

				# strong buff
				if status[2]:
					good = self.remove_type(choices, self.intenses) # remove slayers,etc
					good = self.remove_type(good, self.strongs) # remove intense buffs
					return self.check_if_already(good, info, choices)

				# other
				for i in [self.intenses, self.strongs, self.goods]: # remove all good buffs
					good = self.remove_type(good, i)
				return self.check_if_already(good, info, choices)

			else: # case its a normal item
				pass

			# add class exclusives
			good = copy.deepcopy(choices)
			good += self.buffs[itemtype][status[0]+"-exclusive"]
			good = self.remove_all(good)
			return random.choice(good)

		### Case Shield ###
		if itemtype == 'shield':
			goods = ['Fast Guard Attack','Guard move Speed up','Spartan Uppercut']
			
			if is_sp:
				if status[3]:
					return self.check_if_already(choices, info, choices) # can get anything
				else:
					good = copy.deepcopy(choices)
					good = self.remove_type( good, goods ) # remove good shield buffs
					return self.check_if_already(good, info, choices)
			else:
				good = copy.deepcopy(choices)
				good = self.remove_type(choices, goods) #remove good shield buffs
				good = self.remove_all(good)
				return self.check_if_already(good, info, choices)

		### Case Accessory ###
		if itemtype == 'acc':
			if is_sp:

				if status[2]:
					good = []
					for x in choices: # only lv 3 buffs
						for y in self.goods:
							if y.lower() in x.lower():
								good.append(x)
					return self.check_if_already(good, info, choices)

				good = copy.deepcopy(choices)
				good = self.remove_type(good, self.goods) # remove lv3 buffs
				return self.check_if_already(good, info, choices)
			else:
				good = copy.deepcopy(choices)
				good = self.remove_all(good)
				return self.check_if_already(good, info, choices)

	def check_if_already(self, goodlist, info, backup):
		try:
			tries = 5
			for a in range(tries):
				isgood = True
				test = random.choice(goodlist)
				for x in info['buffs']:
					if test.lower() in x.lower():
						isgood = False
					if ''.join(test.lower().split()) in x.lower():
						isgood = False
				if isgood:
					break
			return test
		except:
			try:
				return random.choice(goodlist)
			except:
				return random.choice(backup)

	def remove_all(self, good):
		for i in [self.intenses, self.strongs, self.goods]: # remove all good buffs
			good = self.remove_type(good, i)
		return good

	def remove_type(self, mylist, _type):
		newlist = copy.deepcopy(mylist)
		for x in newlist:
			for y in _type:
				if y.lower() in x.lower():
					try:
						newlist.remove(x)
					except: pass
		return newlist

	def correct_weight(self, itemtype, is_sp):
		# Decide what is the max or min weight of item for choices
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
		# returns tuple (class, is_sp, is_high, is_super, is_intense)

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