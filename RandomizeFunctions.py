import json
import math
import random

import LoadLocationData


def getOptionsForItemModifications():
	return ["Replace Custom","Replace Healing","Replace Valuable","Replace Ball"]

def checkIfReplacementsConfigured(inputFlags):
	options = getOptionsForItemModifications()
	for option in options:
		if option in inputFlags:
			return True
	return False

def FlagCheckType(type, inputFlags):
	flagExtend = "Replace " + type
	if flagExtend in inputFlags:
		return True

	return False

def HandleItemReplacement(reachable, inputFlags):
	replacementFile = None

	containsAny = checkIfReplacementsConfigured(inputFlags)

	if containsAny:
		item_replacement = open("Config/ItemReplacement.json")
		replacements = item_replacement.read()
		replacement_data = json.loads(replacements)
		replacementFile = {}
		for replacement_item in replacement_data:
			replacement_item_name = replacement_item["item"]
			replacement_replacement = replacement_item["replacement"]
			replacement_type = replacement_item["type"]

			replacement_percent = 100
			use_replacement_percent = False

			if use_replacement_percent and "chance" in replacement_item:
				replacement_percent = replacement_item["chance"]

			useReplacement = FlagCheckType(replacement_type, inputFlags)
			if useReplacement:
				replacementFile[replacement_item_name] = (replacement_replacement, replacement_percent)

	if 'Delete Fly' in inputFlags:
		if replacementFile is None:
			replacementFile = {}

		replacementFile["Fly"]: "BERRY"

	changes = {}

	if replacementFile is not None:
		for i in reachable.values():
			replaced = ReplaceItem(i, replacementFile)
			if replaced:
				changes[i.Name] = i.item

	return changes


def ReplaceItem(item, replaceFile):
	replaced = False
	if item.isItem():
		while item.item in replaceFile.keys():
			if item.item in replaceFile.keys():
				replacement = replaceFile[item.item]
				item_chance = replacement[1]
				if item_chance >= random.random()*100:
					item.item = replacement[0]
					replaced = True
				else:
					break
	return replaced

def IterateRequirements(location, locations, known, partial_known=[]):
	addedLocation=[]
	addedFlag=[]
	addedItem=[]

	for req in location.LocationReqs:
		reqData = list(filter(lambda x: x.Name == req, locations))
		if len(reqData) == 0:
			print("Could not find LOCATION:",req)
			return [],[],[]
		#Currently assume if more than one, that they are options
		allRequiredLoc = []
		allRequiredFlag = []
		allRequiredItem = []
		for data in reqData:
			if data in known:
				allRequiredLoc.extend(data.LocationReqs)
				allRequiredFlag.extend(data.FlagReqs)
				allRequiredItem.extend(data.ItemReqs)
				continue
			if data in partial_known:
				allRequiredLoc.extend(data.LocationReqs)
				allRequiredFlag.extend(data.FlagReqs)
				allRequiredItem.extend(data.ItemReqs)
				continue
			else:
				partial_known.append(data)
			locs,flags,items = IterateRequirements(data, locations,known, partial_known)

			# Only add one instance from requirements

			allRequiredLoc.extend(locs)
			allRequiredFlag.extend(flags)
			allRequiredItem.extend(items)
			known.append(data)

			allRequiredLoc.extend(data.LocationReqs)
			allRequiredFlag.extend(data.FlagReqs)
			allRequiredItem.extend(data.ItemReqs)



		for x in allRequiredLoc:
			if x not in addedLocation and (len(reqData)==1 or allRequiredLoc.count(x) == len(reqData)):
				addedLocation.append(x)

		for x in allRequiredFlag:
			if x not in addedFlag and (len(reqData) == 1 or allRequiredFlag.count(x) == len(reqData)):
				addedFlag.append(x)

		for x in allRequiredItem:
			if x not in addedItem and (len(reqData) == 1 or allRequiredItem.count(x) == len(reqData)):
				addedItem.append(x)

	for flagSet in location.FlagReqs:
		reqData = list(filter(lambda x: flagSet in x.FlagsSet, locations))
		allRequiredLoc = []
		allRequiredFlag = []
		allRequiredItem = []
		for data in reqData:
			if data in known:
				allRequiredLoc.extend(data.LocationReqs)
				allRequiredFlag.extend(data.FlagReqs)
				allRequiredItem.extend(data.ItemReqs)
				continue
			if data in partial_known:
				allRequiredLoc.extend(data.LocationReqs)
				allRequiredFlag.extend(data.FlagReqs)
				allRequiredItem.extend(data.ItemReqs)
				continue
			else:
				partial_known.append(data)
			locs, flags, items = IterateRequirements(data, locations, known, partial_known)

			# Only add one instance from requirements

			allRequiredLoc.extend(locs)
			allRequiredFlag.extend(flags)
			allRequiredItem.extend(items)
			known.append(data)

			allRequiredLoc.extend(data.LocationReqs)
			allRequiredFlag.extend(data.FlagReqs)
			allRequiredItem.extend(data.ItemReqs)

		for x in allRequiredLoc:
			if x not in addedLocation and (len(reqData) == 1 or allRequiredLoc.count(x) == len(reqData)):
				addedLocation.append(x)

		for x in allRequiredFlag:
			if x not in addedFlag and (len(reqData) == 1 or allRequiredFlag.count(x) == len(reqData)):
				addedFlag.append(x)

		for x in allRequiredItem:
			if x not in addedItem and (len(reqData) == 1 or allRequiredItem.count(x) == len(reqData)):
				addedItem.append(x)

	parents = list(filter(lambda x: location in x.Sublocations, locations))
	while parents is not None and len(parents) > 0:
		parent = parents[0]
		addedItem.extend(parent.ItemReqs)
		addedFlag.extend(parent.FlagReqs)
		addedLocation.extend(parent.LocationReqs)

		addedLocation.append(parent.Name)

		parents = list(filter(lambda x: parent in x.Sublocations, locations))


		#addedLocation.append(reqData.Name)

	addedItem.extend(location.ItemReqs)
	addedFlag.extend(location.FlagReqs)
	addedLocation.extend(location.LocationReqs)

	return addedLocation,addedFlag,addedItem


class HintMessage():
	type=None
	item=None
	secondary=None
	helpful=None
	messages=None

	def __init__(self, type, item, secondary, helpful):
		self.type = type
		self.item = item
		self.secondary = secondary
		self.helpful = helpful
		self.messages = []

	def __str__(self):
		return str(self.item)+" "+str(self.type)+" "+self.secondary

	def toMessages(self, length, parts):
		m_l = math.floor((length - 2) / 2)
		require_message = " needs"
		r_l = len(require_message)+1
		mf_l = m_l-r_l


		if self.type == "nothing":
			if len(self.secondary) > 14:
				message1 = self.secondary[0:m_l-1]+"-"
				message2 = self.secondary[m_l-1:]+" is free!"
			else:
				message1 = self.secondary
				message2 = "is free!"
		elif self.type == "requires" or self.type == "in":
			if len(self.secondary)>m_l and len(self.item)>m_l:
				message1 = "X"+self.item[0:m_l-1]
				message2 = "Y"+self.secondary[0:m_l-1]
			elif len(self.secondary) > m_l and len(self.item) > mf_l:
				message1 = self.item+"."
				message2 = self.secondary[0:m_l]
			elif len(self.secondary) > m_l:
				message1 = self.item + " " + "needs"
				message2 = self.secondary[0:m_l]
			elif len(self.item) > m_l and len(self.secondary)>mf_l:
				message1= "."+self.item
				message2= self.secondary[0:m_l]
			elif len(self.item) > m_l:
				message1 = self.item[0:m_l]
				message2 = "needs "+self.secondary
			elif len(self.item) > mf_l:
				message1 = self.item
				message2 = "needs " + self.secondary
			elif len(self.secondary) > mf_l:
				message1 = self.item + " needs"
				message2 = self.secondary
			else:
				message1 = self.item + " needs"
				message2 = self.secondary

		else:
			message1 = "Incomplete"
			message2= "Hint"

		while len(message1) + len(message2)  < length - 1:
			if len(message1) > len(message2):
				message2 += " "
			else:
				message1 += " "

		self.messages = [message1, message2]
		return True


class AddrObject:
	start = None
	end = None
	item = None
	length = None
	commands = None
	messages = []

	def __init__(self, item, start, end, commands):
		self.item = item
		self.start = start
		self.end = end
		self.commands = commands
		self.length = self.end - self.start


def PrepareHintMessages(addressData, hints, available):
	# [{"start": 1870726, "end": 1870758
	#	 , "name": "MasterBall", "commands": 2},

	addObjects = []
	for address in addressData.keys():
		addObj = addressData[address]
		addObjects.append(AddrObject(address, addObj["start"], addObj["end"], addObj["commands"]))

	avItems = []
	for x in available:
		avItems.append(x.replace("_", "").replace(" ", "").upper())

	# {type=None,	item=None,	secondary=None,	helpful=None}
	validAddresses = list(filter(lambda x: x.length > 2 and x.commands == 2 and x.item.upper() in avItems, addObjects))
	random.shuffle(validAddresses)

	useHints = []

	random.shuffle(hints)
	for addr in validAddresses:
		if len(hints) == 0:
			break
		currentHint = hints.pop(0)
		success = currentHint.toMessages(addr.length, addr.commands)
		if success:
			useHints.append((addr,currentHint))

	#Debug Info
	for hint in useHints:
		hintAddr = hint[0]
		hintDetail = hint[1]

		print("Item:",hintAddr.item, "Messages:", hintDetail.messages)


	return useHints

def GenerateHintMessages(spoiler, trashSpoiler, locations):
	useful_hint_chance = 100

	#AllLocations = LoadLocationData.LoadDataFromFolder(".", None, None, modifiers, flags)
	locationList = LoadLocationData.FlattenLocationTree(locations)

	known = []
	for location in locationList:

		addedLoc, addedFlag, addedItem = IterateRequirements(location,locationList, known, partial_known=[])

		for req in addedLoc:
			if req not in location.LocationReqs:
				location.LocationReqs.append(req)

		for req in addedItem:
			if req not in location.ItemReqs:
				location.ItemReqs.append(req)

		for req in addedFlag:
			if req not in location.FlagReqs:
				location.FlagReqs.append(req)

	to_check_location = ["Elite Four", "Whirl Islands",
						 "Tin Tower", "VS HoOh", "Rocket Base", "Ruins of Alph",
						 "Cianwood City", "Blackthorn City", "Cinnabar Island"
						 ]
	no_free_locations = []

	to_check_flag = ["Kanto Power Restored", "Mahogany Rockets Defeated",
					 "Became Champion", "Power Plant", "Beat Team Rocket"]
	no_free_flag = []

	to_check_item = ["Flash","Strength","Whirlpool","Waterfall",
					 "Secret Potion","Basement Key"]
	no_free_item = []

	itemToReq=[]

	notValidHints = ["Bicycle","Fly","Storm Badge","Berry Trees","Hidden Items","Timed Events",
					 "Kanto Mode"]

	spoiler_keys = list(spoiler.keys())
	for key in spoiler_keys:
		location_name = spoiler[key]
		result = list(filter(lambda x: x.Name == location_name, locationList))
		if len(result) != 1:
			print("Should be only one result")
		else:
			found_result = result[0]

			#for ix in found_result.LocationReqs:
			#	if ix not in notValidHints:
			#		itemToReq.append((key,ix))

			for ix in found_result.ItemReqs:
				if ix not in notValidHints:
					itemToReq.append(HintMessage("requires",key,ix,True))

			for ix in found_result.FlagReqs:
				if ix not in notValidHints:
					itemToReq.append(HintMessage("requires",key,ix,True))


			print(key, location_name, found_result.ItemReqs, found_result.FlagReqs)
			for i in to_check_location:
				if i in found_result.LocationReqs:
					no_free_locations.append(i)
			for i in to_check_flag:
				if i in found_result.FlagReqs:
					no_free_flag.append(i)
			for i in to_check_item:
				if i in found_result.ItemReqs:
					no_free_item.append(i)

			parent = found_result
			parents = list(filter(lambda x: found_result in x.Sublocations, locations))
			while parents is not None and len(parents) > 0:
				parent = parents[0]
				parents = list(filter(lambda x: parent in x.Sublocations, locations))

			# Refactor Map files to use 'Hint Name' for topmost parent to remove some ambiguity / longer names
			itemToReq.append(HintMessage("in",key,parent.HintName,True))
			#print("Mostly parent of:",key,"is",parent.HintName)

	for x in no_free_locations:
		if x in to_check_location:
			to_check_location.remove(x)

	for x in no_free_item:
		if x in to_check_item:
			to_check_item.remove(x)

	for x in no_free_flag:
		if x in to_check_flag:
			to_check_flag.remove(x)


	for i in to_check_location:
		itemToReq.append(HintMessage("nothing",None,i,True))
	for i in to_check_flag:
		itemToReq.append(HintMessage("nothing",None,i,True))
	for i in to_check_item:
		itemToReq.append(HintMessage("nothing",None,i,True))

	return itemToReq







