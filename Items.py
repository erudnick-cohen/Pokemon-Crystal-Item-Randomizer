import yaml

def makeItemCodeDict():
	#hardcoding key item lookups for now, pass as parameter in future
	keyItemMap = {'Surf':'HM_SURF', 'Squirtbottle':"SQUIRTBOTTLE", 'Flash':'HM_FLASH', 'Mystery Egg':'MYSTERY_EGG', 'Cut':'HM_CUT'}
	itemCodeDict = {}
	
	#progress items
	filestream = open('ItemData/ProgressItems.yml')
	data = filestream.read()
	yamlTree = yaml.load(data)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"]
	
	#trash items
	filestream = open('ItemData/trashItems.yml')
	data = filestream.read()
	yamlTree = yaml.load(data)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"]
		
	#define lookup function
	def lookupItem(item,isBall):
		if item not in itemCodeDict:
			if item in keyItemMap:
				item = keyItemMap[item]
			if(isBall):
				return "itemball "+item
			else:
				return "verbosegiveitem "+item
		else:
			return itemCodeDict[item]
	return lookupItem

def makeItemTextDict():
	itemCodeDict = {}
	
	#progress items
	filestream = open('ItemData/ProgressItems.yml')
	data = filestream.read()
	yamlTree = yaml.load(data)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Name"]
			
	#trash items
	filestream = open('ItemData/trashItems.yml')
	data = filestream.read()
	yamlTree = yaml.load(data)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Name"].upper()
		
	#define lookup function
	def lookupItem(item):
		if item not in itemCodeDict:
			return item.replace("TM_","").replace("_", " ")
		else:
			return itemCodeDict[item]
	return lookupItem
			