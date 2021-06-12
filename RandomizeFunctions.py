import json


def HandleItemReplacement(reachable, inputFlags):
	replacementFile = None
	if ('Replace Items' in inputFlags):
		item_replacement = open("ItemReplacement.json")
		replacements = item_replacement.read()
		replacement_data = json.loads(replacements)
		replacementFile = {}
		for replacement_item in replacement_data:
			replacement_item_name = replacement_item["item"]
			replacement_replacement = replacement_item["replacement"]
			replacementFile[replacement_item_name] = replacement_replacement

	elif 'Delete Fly' in inputFlags:
		replacementFile = {"Fly": "BERRY"}

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