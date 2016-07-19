import os
import json
import random
import threading

from Buffs import BUFFS

class Backend(object):
	CACHE_FILE = "cache.json"

	classes  = ["warrior","cleric","mage"]
	strongs  = ['aid','slayer','Anti-Guard']
	intenses = ['intens','far','reach','super','fast','longer']
	goods    = ['3','effect','weight','crush']

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

	def get_random_item(self, itemtype):
		# item_entry =  (item name, item info, random buff)
		# return 3 item entries (normal, normal, prem or sp)
		status = self.pick_random_type()
		print "is sp: "+repr(status[1])

		ITEMS = []

		for x in [1,2,3]:

			# generate item choices based on weight
			if itemtype in ['shield','acc']:
				item_choices = self.data[itemtype]
			else:
				item_choices = self.data[status[0]][itemtype]
			_choices = list([ z for z in item_choices ])
			good = {}

			for y in _choices:
				data = item_choices[y]
				is_sp = False

				# normal premiums
				if x in [1,2]:
					mx_w = self.correct_weight(itemtype, False) - 1
					if data['weight'] <= mx_w:
						good[y] = data

				# super premiums
				else:
					is_sp = True
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

			rand_buff = self.get_random_buff(status[0], itemtype, status, good[item_name]['buffs'], is_sp)

			# add to items to display
			ITEMS.append( [item_name, good[item_name], rand_buff])

		for x in ITEMS:
			print x[0], x[-1]

		return ITEMS

	def get_random_buff(self, classname, itemtype, status, has_buffs, is_sp):
		choices = self.buffs[itemtype]

		if itemtype in ['armor','weapon','helmet']:
			random.shuffle(self.buffs[itemtype]['all'])
			good = []

			# intensify buff
			try:
				if status[4] and is_sp:
					good = []
					for x in choices['all']:
						for y in self.intenses:
							if y in x.lower():
								good.append(x)
				return self.filter_if_there(good, has_buffs, self.buffs[itemtype]['all'])
			except Exception as e:
				print "Error on intense: " + str(e)

			# slayer worthy
			try:
				if status[3] and is_sp:
					for x in choices['all']:
						for y in self.strongs:
							if y in x.lower():
								good.append(y)
					return self.filter_if_there(good, has_buffs, self.buffs[itemtype]['all'])
			except Exception as e:
				print "Error on Slayers: " + str(e)

			# strong buff
			try:
				if status[1] or status[2]:
					if is_sp:
						good = []
						for x in choices['all']:
							for y in self.goods:
								if y in x.lower(): good.append(x)
										
						return self.filter_if_there(good, has_buffs, self.buffs[itemtype]['all'])
			except Exception as e:
				print "Error on Strong: " + str(e)

			# other
			try:
				good = choices['all']
				for x in good:
					for y in self.goods:
						if y.lower() in x:
							good.remove(x)

				for x in good:
					if x in self.strongs or x in self.intenses:
						good.pop(good.index(x))
				good += self.buffs[itemtype][classname+'-exclusive']
				random.shuffle(good)
				return self.filter_if_there(good, has_buffs, self.buffs[itemtype]['all'])
			except Exception as e:
				print "Error on Normal: " + str(e)

		### Case Shield ###
		if itemtype == 'shield':
			goods = ['Fast Guard Attack','Guard move Speed up','Spartan Uppercut']
			random.shuffle(goods)
			if status[3]:
				return self.filter_if_there(good, has_buffs)
			else:
				random.shuffle(choices)
				while True:
					buff = random.choice(choices)
					if buff not in goods: break
				return self.filter_if_there([buff], has_buffs, self.buffs[itemtype])

		if itemtype == 'acc':
			if status[3] and is_sp:
				good = [x for x in choices if '3' in x.lower() or 'weight' in x.lower()]
				return self.filter_if_there(good, has_buffs, self.buffs[itemtype])
			else:
				good = [x for x in choices if '3' not in x.lower() or 'weight' not in x.lower()]
				return self.filter_if_there(good, has_buffs, self.buffs[itemtype])

	def filter_if_there(self, good, has_buffs, others):
		try:
			random.shuffle(good)
			#good = self.remove_strongs(good)
			for x in range(5):
				has = False
				c = random.choice(good)
				for x in has_buffs:
					if c.lower() in x.lower():
						pass
					else: has = True
				if has: break
			return c
		except Exception as e:
			new = self.remove_strongs(others)
			return random.choice(new)

	def remove_strongs(self, others):
		for x in others:
			has_removed = False
			for y in self.intenses:
				if y.lower() in x.lower():
					others.remove(x)
					has_removed = True
			for y in self.strongs:
				if y.lower() in x.lower():
					if not has_removed:
						others.remove(x)
						has_removed = True
			for y in self.goods:
				if y.lower() in x.lower():
					if not has_removed:
						others.remove(x)
						has_removed = True
		return others


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