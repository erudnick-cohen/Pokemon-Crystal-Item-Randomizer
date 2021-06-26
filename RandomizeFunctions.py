import json
import random

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
			if "chance" in replacement_item:
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