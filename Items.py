import yaml
import csv

def makeItemCodeDict():
	#hardcoding key item lookups for now, pass as parameter in future
	keyItemMap = {'Surf':'HM_SURF', 'Squirtbottle':"SQUIRTBOTTLE", 'Flash':'HM_FLASH', 'Mystery Egg':'MYSTERY_EGG', 'Cut':'HM_CUT','Strength': 'HM_STRENGTH','Secret Potion':'SECRETPOTION', 'Red Scale':'RED_SCALE','Whirlpool': 'HM_WHIRLPOOL', 'Card Key': 'CARD_KEY', 'Basement Key':'BASEMENT_KEY', 'Waterfall':'HM_WATERFALL','S S Ticket':'S_S_TICKET', 'Machine Part': 'MACHINE_PART','Lost Item':'LOST_ITEM','Bicycle':'BICYCLE', 'Pass':'PASS'}
	itemCodeDict = {}
	
	#progress items
	filestream = open('ItemData/ProgressItems.yml')
	data = filestream.read()
	yamlTree = yaml.load(data)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"].upper()
	
	#trash items
	filestream = open('ItemData/trashItems.yml')
	data = filestream.read()
	yamlTree = yaml.load(data)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"]
		
	#define lookup function
	def lookupItem(item,isBall,isSpecial):
		if item not in itemCodeDict:
			if item in keyItemMap:
				item = keyItemMap[item]
			if(isBall):
				return "itemball "+item
			elif not isSpecial:
				return "verbosegiveitem "+item
			else:
				return item
		else:
			return itemCodeDict[item]
	return lookupItem

def makeRawItemCodeDict():
	#hardcoding key item lookups for now, pass as parameter in future
	keyItemMap = {'Surf':'HM_SURF', 'Squirtbottle':"SQUIRTBOTTLE", 'Flash':'HM_FLASH', 'Mystery Egg':'MYSTERY_EGG', 'Cut':'HM_CUT','Strength': 'HM_STRENGTH','Secret Potion':'SECRETPOTION', 'Red Scale':'RED_SCALE','Whirlpool': 'HM_WHIRLPOOL', 'Card Key': 'CARD_KEY', 'Basement Key':'BASEMENT_KEY', 'Waterfall':'HM_WATERFALL','S S Ticket':'S_S_TICKET', 'Machine Part': 'MACHINE_PART','Lost Item':'LOST_ITEM','Bicycle':'BICYCLE','Pass':'PASS'}
	itemCodeDict = {}
	
	#progress items
	filestream = open('ItemData/ProgressItems.yml')
	data = filestream.read()
	yamlTree = yaml.load(data)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"].upper()
	
	#trash items
	filestream = open('ItemData/trashItems.yml')
	data = filestream.read()
	yamlTree = yaml.load(data)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"]	
	rawTable = {}
	with open('ItemValues.csv', newline='') as csvfile:
		reader = csv.reader(csvfile)
		for i in reader:
			print(i)
			if(len(i)>0):
				rawTable[i[0]] = int(i[1])
			
	def lookupItemCode(item):
		if item not in itemCodeDict:
			if item in keyItemMap:
				item = keyItemMap[item]
		return rawTable[item]
	return lookupItemCode
	
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
			