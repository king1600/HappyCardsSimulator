import urllib2
import bs4
import threading
import multiprocessing
import json
import copy
import re

class Fetcher(object):
	THREADS = int(multiprocessing.cpu_count())
	BUFFER  = 8192
	FILENAME= "test.json"

	LINKS   = {
		'weapon':{
			'warrior':"http://happywars.wikia.com/wiki/Warrior_Weapons",
			'mage':"http://happywars.wikia.com/wiki/Mage_Weapons",
			'cleric':"http://happywars.wikia.com/wiki/Cleric_Weapons"
		},
		'armor':{
			'warrior':"http://happywars.wikia.com/wiki/Warrior_Armor",
			'mage':"http://happywars.wikia.com/wiki/Mage_Armor",
			'cleric':"http://happywars.wikia.com/wiki/Cleric_Armor"
		},
		'helmet':{
			'warrior':"http://happywars.wikia.com/wiki/Warrior_Helmets",
			'mage':"http://happywars.wikia.com/wiki/Mage_Helmets",
			'cleric':"http://happywars.wikia.com/wiki/Cleric_Helmets"
		},
		'shield':"http://happywars.wikia.com/wiki/Shields",
		'acc':"http://happywars.wikia.com/wiki/Accessory_List"
	}

	def __init__(self):
		self.create_tables()

		classes = ['warrior','cleric','mage']
		
		print "Scrapping, Parsing and Sorting class info..."
		for x in classes:
			print "[*] "+x
			for y in ['weapon','armor','helmet']:
				self.load_item_data( y, x )

		print "Getting Shield and Accessory info..."
		self.load_item_data('shield','something')
		self.load_item_data('acc','something')
		
		print "Done!"
		self.save()

	def save(self):
		with open('cache.json','w') as f:
			f.write( json.dumps(self.data, indent=4, sort_keys=True))

	def create_tables(self):
		items = {
			'weapon':{},
			'armor':{},
			'helmet':{}
		}
		self.data = {
			'warrior':copy.deepcopy(items),
			'mage':   copy.deepcopy(items),
			'cleric': copy.deepcopy(items),
			'shield': {},
			'acc':    {}
		}

	def load_item_data(self, itemtype, classname):
		# Choose URL
		if itemtype in ['shield','acc']:
			url = self.LINKS[ itemtype ]
		else:
			url = self.LINKS[ itemtype ][ classname ]

		# Parse URL data
		url_data = urllib2.urlopen(url).read()
		soup = bs4.BeautifulSoup( url_data ,'html.parser')

		# Sort url data
		div = [d for d in soup.find_all('div') if d.has_attr('id') and 'mw-content-text' in d['id']]
		table = [t for t in div[0].find_all('table') if t.has_attr('class') and 'wikitable' in t['class']]
		item_entries = table[0].find_all('tr')
		item_entries.pop(0) # Column head dedscription

		# create item entries
		for item in item_entries:
			info = [i for i in item.find_all('td')]

			if itemtype == 'weapon':
				data = self.create_weapon_data(classname, info)
			elif itemtype == 'armor':
				data = self.create_armor_data(classname, info)
			elif itemtype == 'helmet':
				data = self.create_helmet_data(classname, info)
			elif itemtype == 'shield':
				data = self.create_shield_data(classname, info)
			elif itemtype == 'acc':
				data = self.create_acc_data(classname, info)
			else:
				pass

			if itemtype in ['shield','acc']:
				self.data[itemtype][data['name']] = data
			else:
				self.data[classname][itemtype][data['name']] = data

			#break #-debugging

	""" Data filter functions """

	def create_acc_data(self, cname, info):
		item_data = self.create_item_data(info)

		item_data['slots'] = int(info[3].text)	
		item_data['buffs'] = [b for b in info[4].find_all('span')[0] if b not in [u"<br/>",u"None"]]
		item_data['buffs'] = self.filter_buffs(item_data['buffs'])

		return item_data

	def create_shield_data(self, cname, info):
		item_data = self.create_item_data(info)

		item_data['guard'] = int(self.filter_range(info[3].text))
		item_data['mguard'] = int(self.filter_range(info[4].text))
		item_data['guard_10'] = int(self.filter_range(info[5].text))
		item_data['mguard_10'] = int(self.filter_range(info[6].text))
		item_data['slots'] = int(info[7].text)
		# get array of buffs
		item_data['buffs'] = [b for b in info[8].find_all('span')[0] if b not in [u"<br/>",u"None"]]
		item_data['buffs'] = self.filter_buffs(item_data['buffs'])

		return item_data

	def create_helmet_data(self, cname, info):
		# helmet has same sorting as armor
		return self.create_armor_data(cname, info)

	def create_armor_data(self, cname, info):
		item_data = self.create_item_data(info)

		item_data['def'] = int(self.filter_range(info[3].text))
		item_data['mdef'] = int(self.filter_range(info[4].text))
		item_data['def_10'] = int(self.filter_range(info[5].text))
		item_data['mdef_10'] = int(self.filter_range(info[6].text))
		item_data['slots'] = int(info[7].text)
		# get array of buffs
		item_data['buffs'] = [b for b in info[8].find_all('span')[0] if b not in [u"<br/>",u"None"]]

		item_data['buffs'] = self.filter_buffs(item_data['buffs'])

		return item_data

	# Create Weapon Dict
	def create_weapon_data(self, cname, info):
		item_data = self.create_item_data(info)

		if cname == 'mage':
			item_data['base_attack'] = int(self.filter_range(info[3].text))
			item_data['lv10_attack'] = int(self.filter_range(info[5].text))
			item_data['slots']       = int(info[7].text)
			item_data['magic_base']  = int(self.filter_range(info[4].text))
			item_data['magic_10']    = int(self.filter_range(info[6].text))
			# get array of buffs
			try:
				item_data['buffs'] = [re.sub(r'[^\w]','',b) for b in info[8].find_all('span')[0] if b not in [u"<br/>",u"None"]]
			except:
				item_data['buffs'] = [info[8].text]
			item_data['buffs'] = self.filter_buffs(item_data['buffs'])

		else:			
			item_data['base_attack'] = int(self.filter_range(info[3].text))
			item_data['lv10_attack'] = int(self.filter_range(info[4].text))
			item_data['slots']       = int(info[5].text)
			item_data['magic_base']  = 0
			item_data['magic_10']    = 0
			# get array of buffs
			item_data['buffs'] = [b for b in info[6].find_all('span')[0] if b not in [u"<br/>",u"None"]]
			item_data['buffs'] = self.filter_buffs(item_data['buffs'])

		return item_data # return completed data

	def filter_range(self, text):
		lowest = True
		if lowest: one = 0
		else: one = 1

		if '?' in str(text): return 0

		if '(+' in str(text):
			first_num = str(text).split('(+')[0]
			sec_num = str(text).split('(+')[1].split(')')[0]
			return int(first_num) + int(sec_num)

		if '-' in str(text):
			t = str(text).split('-')[one]
		else:
			t = str(text)

		if '+' in t:
			nums = re.findall('\d+',t)
			done = 0
			for x in nums:
				done += int(x)
			return done
		return t

	def filter_buffs(self, buffs):
		new = []
		for b in buffs:
			good = True
			try:
				if str(b) == "<br/>": good = False
			except: pass
			try:
				if good:
					new.append(re.sub(r'[^\w]','',b))
			except: pass
		return new

	def create_item_data(self, info):
		item_data = {}
		item_data['image']  = info[0].find_all('a')[0]['href']
		item_data['name']   = info[1].text
		item_data['weight'] = int(info[2].text)
		return item_data

	""" Thread creation functions """

	def build_thread(self, func, ref=False, *args):
		thread = threading.Thread(target=func, args=args)
		thread.daemon = True
		thread.start()

		# return thread reference
		if ref: return thread

	# create normal thread
	def create_thread(self, func, *args):
		self.build_thread(func, False, args)

	# create thread and return reference
	def thread_with_ref(self, func, *args):
		return self.build_thread(func, True, args)

	# split list evenly
	def chunk(self, l, n):
		for i in range(0, len(l), n):
			yield l[i:i+n]

if __name__ == '__main__':
	Fetcher()