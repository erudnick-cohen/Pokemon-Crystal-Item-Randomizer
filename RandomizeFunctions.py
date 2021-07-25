import json
import math
import random

import LoadLocationData


def getOptionsForItemModifications():
	return ["Replace Custom", "Replace Healing", "Replace Valuable", "Replace Ball"]


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
				if item_chance >= random.random() * 100:
					item.item = replacement[0]
					replaced = True
				else:
					break
	return replaced


def IterateRequirements(location, locations, known, partial_known=[]):
	addedLocation = []
	addedFlag = []
	addedItem = []

	for req in location.LocationReqs:
		if req == "Impossible":
			continue
		reqData = list(filter(lambda x: x.Name == req, locations))
		if len(reqData) == 0:
			print("Could not find LOCATION:", req)
			return [], [], []
		# Currently assume if more than one, that they are options
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

		# allRequiredLoc.extend(data.LocationReqs)
		# allRequiredFlag.extend(data.FlagReqs)
		# allRequiredItem.extend(data.ItemReqs)

		for x in allRequiredLoc:
			if x not in addedLocation and (len(reqData) == 1 or allRequiredLoc.count(x) == len(reqData)):
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

		if len(reqData) > 1:
			print("Handle multiple flag set locations")

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

		addedItem.extend(list(filter(lambda x: x not in addedItem, parent.ItemReqs)))
		addedFlag.extend(list(filter(lambda x: x not in addedFlag, parent.FlagReqs)))
		addedLocation.extend(list(filter(lambda x: x not in addedLocation, parent.LocationReqs)))

		# addedItem.extend(parent.ItemReqs)
		# addedFlag.extend(parent.FlagReqs)
		# addedLocation.extend(parent.LocationReqs)

		if parent.Name not in addedLocation:
			addedLocation.append(parent.Name)

		parents = list(filter(lambda x: parent in x.Sublocations, locations))

	# addedLocation.append(reqData.Name)

	addedItem.extend(list(filter(lambda x: x not in addedItem, location.ItemReqs)))
	addedFlag.extend(list(filter(lambda x: x not in addedFlag, location.FlagReqs)))
	addedLocation.extend(list(filter(lambda x: x not in addedLocation, location.LocationReqs)))

	return addedLocation, addedFlag, addedItem


def PathToItem(item):
	replaceNames = {"BLUE_CARD": "Blue Card",
					"ENGINE_POKEDEX": "Pokedex",
					"OLD_ROD": "Rod",
					"GOOD_ROD": "Rod",
					"SUPER_ROD": "Rod",
					"SILVER_WING": "Silver Wing",
					"ITEMFINDER": "ItemFinder",
					"COIN_CASE": "Coin Case"
					}


	if item in replaceNames:
		return replaceNames[item]
	else:
		return item.replace("_", " ").title()

class Msg:
	text = None
	padding = None
	seperator = None

	def __init__(self):
		self.text = ""
		self.padding = 0
		self.seperator = None

import re

class HintMessage():
	type = None
	item = None
	secondary = None
	helpful = None
	messages = None
	totalLength = None

	def reword(self):
		if self.item is not None:
			self.item = PathToItem(self.item)


	def __init__(self, type, item, secondary, helpful):
		self.type = type
		self.item = item
		self.secondary = secondary
		self.helpful = helpful
		self.messages = []
		self.reword()

	def __str__(self):
		return str(self.item) + " " + str(self.type) + " " + self.secondary



	def toMessages(self, length, parts):
		max_length_per_message = 17

		messages = []
		totalMessageLength = 0

		#types: requires, in, something, nothing

		if self.item is None:
			msg = Msg()
			msg.text = self.secondary
			msg.seperator = 81

			msg2 = Msg()

			if self.type == "somethingi":
				msg2.text = self.secondary+"."
				msg.text = "A champion has"
			elif self.type == "somethingf":
				msg.text = "Champs achieve"
				msg2.text = self.secondary+"."
			elif self.type == "somethingl":
				msg.text = "Heroes go to"
				msg2.text = self.secondary+"."
			elif self.type == "nothingl":
				msg2.text = "is barren."
			elif self.type == "nothingi":
				msg2.text = "is a fools toy."
			elif self.type == "nothingf":
				msg.text = "Fools achieve"
				msg2.text = self.secondary

			messages.append(msg)
			messages.append(msg2)

		else:
			msg1 = Msg()
			msg1.seperator = 79

			msg2 = Msg()
			msg2.seperator = 81
			msg3 = Msg()
			msg3.seperator = 79
			msg4 = Msg()

			if self.type == "requiresf":
				msg1.text = "A hero requires"
				msg2.text = self.secondary
				msg3.text = "to access "
				msg4.text = self.item
			elif self.type == "requiresi":
				msg1.text = "A hero requires"
				msg2.text = self.secondary
				msg3.text = "to access"
				msg4.text = self.item
			elif self.type == "in":
				msg1.text = "A hero finds "
				msg2.text = self.item
				msg3.text = "in " + self.secondary

			messages.append(msg1)
			messages.append(msg2)
			messages.append(msg3)
			messages.append(msg4)

		#Take messages which are too long, and combine them into previous/next messages
		messagesTooLong = list(filter(lambda x: len(x.text)>max_length_per_message, messages))
		for tl in messagesTooLong:
			index = messages.index(tl)
			previousPossible = True
			nextPossible = True
			if index == 0:
				previousPossible = False
			if index == len(messages):
				nextPossible = False

			if previousPossible:
				wordCutLeft = tl.text.split(" ")[0]
				previous = messages[index-1]
				previousLength = len(previous.text)

				if previousLength+len(wordCutLeft)+1 < max_length_per_message:
					previous.text += " " + wordCutLeft
					re.sub("^"+wordCutLeft,"",tl.text)
				else:
					previousPossible = False

			nextPossible = nextPossible and len(tl.text.split(" "))>1

			if nextPossible:
				wordCutRight = tl.text.split(" ")[-1]
				next = messages[index-1]
				nextLength = len(next.text)

				if nextLength+len(wordCutRight)+1 < max_length_per_message:
					next.text = wordCutRight + " " + next.text

					re.sub("^"+wordCutRight,"",tl.text)
				else:
					nextPossible = False

			if not nextPossible and not previousPossible:
				newMessage = Msg()
				wordCutRight = tl.text.split(" ")[-1]
				newMessage.text += wordCutRight
				re.sub(wordCutRight + "$", "", tl.text)

				insertAt = index
				if index == len(messages):
					insertAt = len(messages)
				else:
					newMessage.seperator = 79

				messages.insert(insertAt, newMessage)



		totalMessageLength +=1 #Starting byte
		for m in messages:
			totalMessageLength += len(m.text)
			if m.seperator is not None:
				totalMessageLength += 1

		if totalMessageLength > length:
			return False


		expansionChoices = messages.copy()
		while totalMessageLength < length and len(expansionChoices) > 0:
			chosen = random.choice(expansionChoices)
			if len(chosen.text) + chosen.padding > max_length_per_message:
				expansionChoices.remove(chosen)
				continue
			chosen.padding += 1
			totalMessageLength += 1

		while totalMessageLength < length:
			messages[-1].seperator = 78
			msgBlank = Msg()
			mLength = (length-totalMessageLength)
			if mLength > max_length_per_message:
				mLength = max_length_per_message
			msgBlank.text = ""
			msgBlank.padding += mLength
			messages.append(msgBlank)
			totalMessageLength += mLength

		self.messages = messages
		self.totalLength = totalMessageLength
		return True


class AddrObject:
	start = None
	end = None
	item = None
	length = None
	commands = None
	name = None
	messages = []
	map = None

	def __init__(self, item, start, end, commands, name, map):
		self.item = item
		self.start = start
		self.end = end
		self.commands = commands
		self.length = self.end - self.start
		self.name = name
		self.map = map


def PrepareHintMessages(addressData, hints, available):
	# [{"start": 1870726, "end": 1870758
	#	 , "name": "MasterBall", "commands": 2},

	addObjects = []
	for address in addressData.keys():
		addObj = addressData[address]
		addObjects.append(AddrObject(address, addObj["start"], addObj["end"], addObj["commands"], addObj["name"], addObj["map"]))

	#avItems = []
	#for x in available:
		#avItems.append(x.replace("_", "").replace(" ", "").upper())

	# {type=None,	item=None,	secondary=None,	helpful=None}
	#validAddresses = list(filter(lambda x: x.length > 2 and x.commands == 2 and x.item.upper() in avItems, addObjects))
	# Still in development!
	validAddresses = list(filter(lambda x: x.length > 25, addObjects))
	random.shuffle(validAddresses)

	# test code
	# prints signs possible to be changed sorted by location
	#sortedVer = sorted(validAddresses, key=lambda lc: lc.map)
	#print(sortedVer)

	#for var in sortedVer:
	#	print(var.name, var.map)h




	useHints = []

	random.shuffle(hints)
	for addr in validAddresses:
		if len(hints) == 0:
			break
		success = False
		readd_hints = []
		while not success:
			if len(hints) <= 0:
				break
			currentHint = hints.pop(0)
			success = currentHint.toMessages(addr.length, addr.commands)
			if success:
				useHints.append((addr, currentHint))
			else:
				readd_hints.append(currentHint)
		if not success:
			# Since small ones exist, we may also want to add code somewhere to MERGE hints into one
			# But what to do with the extra and keep the files the same size??
			print("Unable to assign any remaining hints to: "+addr.name)
		if len(readd_hints) > 0:
			for i in readd_hints:
				hints.append(i)
			random.shuffle(hints)

	# Debug Info
	for hint in useHints:
		hintAddr = hint[0]
		hintDetail = hint[1]

	return useHints


def GenerateHintMessages(spoiler, trashSpoiler, locations, criticalTrash, badgeDict):
	useful_hint_chance = 100

	# AllLocations = LoadLocationData.LoadDataFromFolder(".", None, None, modifiers, flags)
	locationList = LoadLocationData.FlattenLocationTree(locations)

	known = []
	for location in locationList:

		addedLoc, addedFlag, addedItem = IterateRequirements(location, locationList, known, partial_known=[])

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
						 "Tin Tower", "VS Ho-Oh", "Rocket Base", "Ruins of Alph",
						 "Cianwood City", "Blackthorn City", "Cinnabar Island",
						 "Route 4", "Fuchsia City", "Pewter City", "Mt Mortar Surf Floor",
						 "Mt Mortar Upper Floor", "Elm's Lab", "Route 26", "Route 27" ]

	# Need message converter when loading these locations

	no_free_locations = []

	to_check_flag = ["Kanto Power Restored", "Mahogany Rockets Defeated","Power Plant", "Beat Team Rocket"]
	no_free_flag = []

	to_check_item = ["Flash", "Strength", "Whirlpool", "Waterfall",
					 "Secret Potion", "Basement Key"]
	no_free_item = []

	itemToReq = []

	notValidHints = ["Bicycle", "Fly", "Storm Badge",
					 "Berry Trees", "Hidden Items", "Timed Events",
					 "Kanto Mode"]

	MAX_HINTS_PER_ITEM = 2

	inverse_trash = {v: k for k, v in trashSpoiler.items()}
	for cTrash in criticalTrash:
		if cTrash in inverse_trash:
			cLocation = inverse_trash[cTrash]
			spoiler[cTrash] = cLocation

	requiredKeys = []
	requiredKeys.extend(list(badgeDict.keys()))

	spoiler_keys = list(spoiler.keys())
	for key in spoiler_keys:

		trash = False
		if key in inverse_trash.keys():
			trash = True

		if key.startswith("TM_"):
			continue

		one_location_hints = []

		location_name = spoiler[key]
		result = list(filter(lambda x: x.Name == location_name, locationList))
		if len(result) != 1:
			print("Should be only one result")
		else:
			found_result = result[0]

			if "Impossible" in found_result.LocationReqs:
				continue

			# for ix in found_result.LocationReqs:
			#	if ix not in notValidHints:
			#		itemToReq.append((key,ix))

			for ix in found_result.ItemReqs:
				if ix not in notValidHints:
					one_location_hints.append(HintMessage("requiresi", key, ix, True))

			for ix in found_result.FlagReqs:
				if ix not in notValidHints:
					one_location_hints.append(HintMessage("requiresf", key, ix, True))

			# print(key, location_name, found_result.ItemReqs, found_result.FlagReqs)
			if not trash:
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
			parents = list(filter(lambda x: found_result in x.Sublocations, locationList))
			unequalHintNames = []
			while parents is not None and len(parents) > 0:
				parent = parents[0]
				if parent.Name != parent.HintName:
					unequalHintNames.append(parent.HintName)
				parents = list(filter(lambda x: parent in x.Sublocations, locationList))

			# Refactor Map files to use 'Hint Name' for topmost parent to remove some ambiguity / longer names
			useHintName = None
			if len(unequalHintNames) == 0:
				useHintName = parent.HintName
			else:
				useHintName = unequalHintNames[0]


			one_location_hints.append(HintMessage("in", key, useHintName, True))

			random.shuffle(one_location_hints)

			added = 0
			while added < MAX_HINTS_PER_ITEM and len(one_location_hints) > 0:
				item_hint = one_location_hints.pop(0)
				itemToReq.append(item_hint)

				added += 1

		# print("Mostly parent of:",key,"is",parent.HintName)

	for x in no_free_locations:
		if x in to_check_location:
			itemToReq.append(HintMessage("somethingl", None, x, True))
			to_check_location.remove(x)

	for x in no_free_item:
		if x in to_check_item:
			itemToReq.append(HintMessage("somethingi", None, x, True))
			to_check_item.remove(x)

	for x in no_free_flag:
		if x in to_check_flag:
			itemToReq.append(HintMessage("somethingf", None, x, True))
			to_check_flag.remove(x)

	for i in to_check_location:
		itemToReq.append(HintMessage("nothingl", None, i, True))
	for i in to_check_flag:
		itemToReq.append(HintMessage("nothingf", None, i, True))
	for i in to_check_item:
		itemToReq.append(HintMessage("nothingi", None, i, True))

	# Reverse lookup some key items and see which are not required

	return itemToReq
