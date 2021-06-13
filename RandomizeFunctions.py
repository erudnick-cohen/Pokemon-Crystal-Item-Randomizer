import json

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

			useReplacement = FlagCheckType(replacement_type, inputFlags)
			if useReplacement:
				replacementFile[replacement_item_name] = replacement_replacement

	if 'Delete Fly' in inputFlags:
		if replacementFile is None:
			replacementFile = {}

		replacementFile["Fly"]: "BERRY"

	if replacementFile is not None:
		for i in reachable.values():
			ReplaceItem(i, replacementFile)


def ReplaceItem(item, replaceFile):
	if item.isItem():
		# print(i.Name)
		# print('item is: '+str(i.item))
		if item.item in replaceFile.keys():
			item.item = replaceFile[item.item]
	return