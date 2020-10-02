import LoadLocationData
import Badge
import RandomizeItemsAssumedFill as RandomizeItems
import RandomizerRom
import PokemonRandomizer
import yaml
import json
import mmap
from collections import defaultdict
import copy
import traceback

def randomizeRom(romPath, goal, flags = [], patchList = [], banList = None, allowList = None, modifiers = [], adjustTrainerLevels = False,adjustRegularWildLevels = False, adjustSpecialWildLevels = False, trainerLVBoost = 0, wildLVBoost = 0, requiredItems = ['Surf', 'Squirtbottle', 'Flash', 'Mystery Egg', 'Cut', 'Strength', 'Secret Potion','Red Scale', 'Whirlpool','Card Key', 'Basement Key', 'Waterfall', 'S S Ticket','Bicycle','Machine Part', 'Lost Item', 'Pass', 'Fly'], plandoPlacements = {}):

	changeListDict = defaultdict(lambda: [])
	extraTrash = []
	for i in modifiers:
		#print(i)
		if 'FlagsSet' in i:
			flags.extend(i['FlagsSet'])
		if 'Changes' in i:
			for j in i['Changes']:
				changeListDict[j['Location']].append(j) 
		if 'AddedItems' in i:
			for j in i['AddedItems']:
				if j not in requiredItems:
					requiredItems.append(j)
			#print(requiredItems)
		if 'AddedTrash' in i:
			extraTrash.extend(i['AddedTrash'])
		if 'NewGamePatches' in i:
			for j in i['NewGamePatches']:
				pfile = open(j)
				ptext = pfile.read()
				patchList.extend(json.loads(ptext))
	print(changeListDict)

	Zephyr = Badge.Badge()
	Zephyr.isTrash = False
	Zephyr.Name = 'Zephyr Badge'
	Zephyr.Code = 27
	Fog = Badge.Badge()
	Fog.isTrash = False
	Fog.Name = 'Fog Badge'
	Fog.Code = 30
	Hive = Badge.Badge()
	Hive.isTrash = False
	Hive.Name = 'Hive Badge'
	Hive.Code = 28
	Plain = Badge.Badge()
	Plain.isTrash = False
	Plain.Name = 'Plain Badge'
	Plain.Code = 29
	Storm = Badge.Badge()
	Storm.isTrash = False
	Storm.Name = 'Storm Badge'
	Storm.Code = 32
	Mineral = Badge.Badge()
	Mineral.isTrash = True
	Mineral.Name = 'Mineral Badge'
	Mineral.Code = 31
	Glacier = Badge.Badge()
	Glacier.isTrash = False
	Glacier.Name = 'Glacier Badge'
	Glacier.Code = 33
	Rising = Badge.Badge()
	Rising.isTrash = False
	Rising.Name = 'Rising Badge'
	Rising.Code = 34
	if('Kanto Mode' in flags):
		Thunder = Badge.Badge()
		Thunder.isTrash = True
		Thunder.Name = 'Thunder Badge'
		Thunder.Code = 37
		Marsh = Badge.Badge()
		Marsh.isTrash = True
		Marsh.Name = 'Marsh Badge'
		Marsh.Code = 40
		Rainbow = Badge.Badge()
		Rainbow.isTrash = True
		Rainbow.Name = 'Rainbow Badge'
		Rainbow.Code = 38
		Soul = Badge.Badge()
		Soul.isTrash = True
		Soul.Name = 'Soul Badge'
		Soul.Code = 39
		Cascade = Badge.Badge()
		Cascade.isTrash = True
		Cascade.Name = 'Cascade Badge'
		Cascade.Code = 36
		Boulder = Badge.Badge()
		Boulder.isTrash = True
		Boulder.Name = 'Boulder Badge'
		Boulder.Code = 35
		Volcano = Badge.Badge()
		Volcano.isTrash = True
		Volcano.Name = 'Volcano Badge'
		Volcano.Code = 41
		Earth = Badge.Badge()
		Earth.isTrash = True
		Earth.Name = 'Earth Badge'
		Earth.Code = 42
		BadgeDict = {'Fog Badge':Fog, 'Zephyr Badge':Zephyr, 'Hive Badge':Hive, 'Plain Badge': Plain, 'Storm Badge': Storm, 'Mineral Badge': Mineral, 'Glacier Badge': Glacier, 'Rising Badge': Rising, 'Thunder Badge': Thunder, 'Marsh Badge' : Marsh, 'Rainbow Badge': Rainbow, 'Soul Badge': Soul, 'Cascade Badge': Cascade,'Boulder Badge': Boulder, 'Volcano Badge': Volcano, 'Earth Badge': Earth}
	else:
		BadgeDict = {'Fog Badge':Fog, 'Zephyr Badge':Zephyr, 'Hive Badge':Hive, 'Plain Badge': Plain, 'Storm Badge': Storm, 'Mineral Badge': Mineral, 'Glacier Badge': Glacier, 'Rising Badge': Rising}

	result = ['Nothing', 'Here']
	while goal not in result[0]:
		try:
			res = LoadLocationData.LoadDataFromFolder(".",banList,allowList,changeListDict)
			progressItems = copy.copy(requiredItems)
			#hardcoding key item lookups for now, pass as parameter in future
			keyItemMap = {'Surf':'HM_SURF', 'Squirtbottle':"SQUIRTBOTTLE", 'Flash':'HM_FLASH', 'Mystery Egg':'MYSTERY_EGG', 'Cut':'HM_CUT','Strength': 'HM_STRENGTH','Secret Potion':'SECRETPOTION', 'Red Scale':'RED_SCALE','Whirlpool': 'HM_WHIRLPOOL', 'Card Key': 'CARD_KEY', 'Basement Key':'BASEMENT_KEY', 'Waterfall':'HM_WATERFALL','S S Ticket':'S_S_TICKET', 'Machine Part': 'MACHINE_PART','Lost Item':'LOST_ITEM','Bicycle':'BICYCLE', 'Pass':'PASS','Fly':'HM_FLY', 'Clear Bell': 'CLEAR_BELL', 'Rainbow Wing':'RAINBOW_WING', 'Pokegear':'ENGINE_POKEGEAR','Radio Card':'ENGINE_RADIO_CARD','Expansion Card':'ENGINE_EXPN_CARD'}
			trashItems = [x for x in res[1] if not x in keyItemMap.values()] #ensure progress items don't sneak into trash list
			trashItems.extend(extraTrash)
			LocationList = res[0]
			print(progressItems)
			result = RandomizeItems.RandomizeItems('None',LocationList,progressItems,trashItems,BadgeDict,inputFlags = flags, plandoPlacements = plandoPlacements )
			if goal not in result[0]:
				print('bad run, retrying')
		except Exception as err:
			print('Failed with error: '+str(err)+' retrying...')
			traceback.print_exc()
	print('-------')
	for j in result[0]:
		i = result[0][j]
		if(i.NormalItem is None and i.isItem()):
			print(i.Name)
	print('-------')
	for j in result[0]:
		i = result[0][j]
		if(i.NormalItem is not None and not i.isItem()):
			print(i.Name)

	yamlfile = open("crystal-speedchoice-label-details.json")
	yamltext = yamlfile.read()
	addressLists = json.loads(yamltext)
	addressData = {}
	for i in addressLists:
		addressData[i['label'].split(".")[-1]] = i
	print(addressData)

	#newTree = PokemonRandomizer.randomizeTrainers(result[0],85,lambda y: monFun(y,1001,85),True,banMap)
	#get furthest item location distance
	maxDist = max(result[2].values())
	f = open(romPath,'r+b')
	romMap = mmap.mmap(f.fileno(),0)
	RandomizerRom.DirectWriteItemLocations(result[0].values(), addressData,romMap,'Progressive Rods' in flags)
	if adjustRegularWildLevels:
		RandomizerRom.WriteWildLevelsToMemory(result[0], result[2],addressData,romMap,wildLVBoost,maxDist)
	if adjustSpecialWildLevels:
		RandomizerRom.WriteSpecialWildToMemory(result[0], result[2],addressData,romMap,wildLVBoost,maxDist)
	if adjustTrainerLevels:
		RandomizerRom.WriteTrainerDataToMemory(result[0],result[2],addressData,romMap,trainerLVBoost,maxDist)
	RandomizerRom.ApplyGamePatches(romMap,patchList)
	#RandomizerRom.WriteTrainerLevels(result[0], result[2],newTree)
	#RandomizerRom.WriteWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
	#RandomizerRom.WriteSpecialWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
	#print(result[2])
	#print(result[1])
	return result
