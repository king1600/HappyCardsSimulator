import json
import os
import random

class Backend(object):
    CACHE_FILE    = "cache.json"
    BUFFER        = 8192
    THREADS       = int(multiprocessing.cpu_count())

    workers       = []
    running       = True

    item_choices  = ["weapon","shield","armor","helmet","accessory"]

    is_spremium   = False
    is_high_buff  = False
    chances       = {
        'sp_on_happy_time':14,
        'high_buff':       90
    }

    def __init__(self):
        self.reader = JSON_Reader(self.CACHE_FILE)
        self.update_db()

        #self.create_thread(self.thread_manager)
        self.pick_random_type()

    def update_db(self):
        self.reader.load_json()
        self.data = self.reader.content

    """ RNG Generator """

    def pick_random_type(self):
        # returns tuple (class, item, is_superpremium)

        # choose random item type and class type


        # is it super_premium?
        self.is_spremium = False
        r_sp_chances = self.random_success(self.chances['sp_on_happy_time'])
        if r_sp_chances[0]: self.is_spremium = True

        print "SP: "+repr(r_sp_chances)

        # does it have high buff?
        self.is_high_buff = False
        r_sp_chances = self.random_success(self.chances['high_buff'])
        if r_sp_chances[0]: self.is_high_buff = True

        print "HB: " + repr(r_sp_chances)

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

    """ Thread functions """

    def create_thread(self, function, *args):
        thread = threading.Thread(target=function, args=args)
        thread.daemon = True
        thread.start()