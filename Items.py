import yaml
import csv

def makeItemCodeDict():
	#hardcoding key item lookups for now, pass as parameter in future
	keyItemMap = {'Surf':'HM_SURF', 'Squirtbottle':"SQUIRTBOTTLE", 'Flash':'HM_FLASH', 'Mystery Egg':'MYSTERY_EGG', 'Cut':'HM_CUT','Strength': 'HM_STRENGTH','Secret Potion':'SECRETPOTION', 'Red Scale':'RED_SCALE','Whirlpool': 'HM_WHIRLPOOL', 'Card Key': 'CARD_KEY', 'Basement Key':'BASEMENT_KEY', 'Waterfall':'HM_WATERFALL','S S Ticket':'S_S_TICKET', 'Machine Part': 'MACHINE_PART','Lost Item':'LOST_ITEM','Bicycle':'BICYCLE', 'Pass':'PASS','Fly':'HM_FLY', 'Clear Bell': 'CLEAR_BELL', 'Rainbow Wing':'RAINBOW_WING', 'Pokegear':'ENGINE_POKEGEAR','Radio Card':'ENGINE_RADIO_CARD','Expansion Card':'ENGINE_EXPN_CARD'}
	itemCodeDict = {}
	
	#progress items
	filestream = open('ItemData/ProgressItems.yml',encoding='utf-8')
	data = filestream.read()
	yamlTree = yaml.load(data, Loader=yaml.FullLoader)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"].upper()
	
	#trash items
	filestream = open('ItemData/TrashItems.yml',encoding='utf-8')
	data = filestream.read()
	yamlTree = yaml.load(data, Loader=yaml.FullLoader)
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

def makeRawItemCodeDict(progRod = False):
	#hardcoding key item lookups for now, pass as parameter in future
	keyItemMap = {'Surf':'HM_SURF', 'Squirtbottle':"SQUIRTBOTTLE", 'Flash':'HM_FLASH', 'Mystery Egg':'MYSTERY_EGG', 'Cut':'HM_CUT','Strength': 'HM_STRENGTH','Secret Potion':'SECRETPOTION', 'Red Scale':'RED_SCALE','Whirlpool': 'HM_WHIRLPOOL', 'Card Key': 'CARD_KEY', 'Basement Key':'BASEMENT_KEY', 'Waterfall':'HM_WATERFALL','S S Ticket':'S_S_TICKET', 'Machine Part': 'MACHINE_PART','Lost Item':'LOST_ITEM','Bicycle':'BICYCLE', 'Pass':'PASS','Fly':'HM_FLY', 'Clear Bell': 'CLEAR_BELL', 'Rainbow Wing':'RAINBOW_WING', 'Pokegear':'ENGINE_POKEGEAR','Radio Card':'ENGINE_RADIO_CARD','Expansion Card':'ENGINE_EXPN_CARD','Zephyr Badge' : 'ENGINE_ZEPHYRBADGE', 'Hive Badge':'ENGINE_HIVEBADGE','Plain Badge':'ENGINE_PLAINBADGE','Fog Badge':'ENGINE_FOGBADGE', 'Storm Badge':'ENGINE_STORMBADGE', 'Mineral Badge':'ENGINE_MINERALBADGE', 'Glacier Badge':'ENGINE_GLACIERBADGE','Rising Badge':'ENGINE_RISINGBADGE', 'Boulder Badge':'ENGINE_BOULDERBADGE','Cascade Badge':'ENGINE_CASCADEBADGE','Thunder Badge':'ENGINE_THUNDERBADGE','Rainbow Badge':'ENGINE_RAINBOWBADGE', 'Soul Badge':'ENGINE_SOULBADGE','Marsh Badge':'ENGINE_MARSHBADGE','Volcano Badge':'ENGINE_VOLCANOBADGE','Earth Badge':'ENGINE_EARTHBADGE'}
	itemCodeDict = {}
	#progress items
	filestream = open('ItemData/ProgressItems.yml',encoding='utf-8')
	data = filestream.read()
	yamlTree = yaml.load(data, Loader=yaml.FullLoader)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"].upper()
	
	#trash items
	filestream = open('ItemData/TrashItems.yml',encoding='utf-8')
	data = filestream.read()
	yamlTree = yaml.load(data, Loader=yaml.FullLoader)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Output"]
	rawTable = {}
	with open('ItemValues.csv', newline='',encoding='utf-8') as csvfile:
		reader = csv.reader(csvfile)
		for i in reader:
			print(i)
			if(len(i)>0):
				if('ROD' in i[0] and progRod):
					rawTable[i[0]] = (int(i[1]), 'Rod')
				else:
					rawTable[i[0]] = (int(i[1]), 'Item')
	with open('FlagValues.csv', newline='',encoding='utf-8') as csvfile:
		reader = csv.reader(csvfile)
		for i in reader:
			print(i)
			if(len(i)>0):
				rawTable[i[0]] = (int(i[1]), 'Flag')
	print(rawTable)
	print(keyItemMap)

	def lookupItemCode(item):
		if item not in itemCodeDict:
			if item in keyItemMap:
				item = keyItemMap[item]
		return rawTable[item]
	return lookupItemCode
	
def makeItemTextDict():
	itemCodeDict = {}
	
	#progress items
	filestream = open('ItemData/ProgressItems.yml',encoding='utf-8')
	data = filestream.read()
	yamlTree = yaml.load(data, Loader=yaml.FullLoader)
	if not yamlTree["Items"] is None:
		for i in yamlTree["Items"]:
			itemCodeDict[i["Name"]] = i["Name"]
			
	#trash items
	filestream = open('ItemData/TrashItems.yml',encoding='utf-8')
	data = filestream.read()
	yamlTree = yaml.load(data, Loader=yaml.FullLoader)
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
			