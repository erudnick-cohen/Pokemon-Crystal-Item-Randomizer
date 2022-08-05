import GenerateWarpData
import LoadLocationData
import Badge
import RandomizeFunctions
import RandomizeItemsAssumedFill as RandomizeItems
import RandomizeItemsBadgesAssumedFill as RandomizeItemsBadges

import RandomizerRom
import PokemonRandomizer
import yaml
import json
import mmap
from collections import defaultdict
import copy
import traceback
import random

def handleBadSpoiler(result, flags):
	spoiler = result[1]
	state = result[0]

	if "Warps" in flags:
		# Debugging points to be aware of, due to bad warp rom at this time
		if "Victory Road Gate "+LoadLocationData.WARP_OPTION not in state:
			pass
		if "Oaks Lab "+LoadLocationData.WARP_OPTION not in state:
			pass

	if len(result) > 6:
		remainingProgressItems = result[6]
		for s in remainingProgressItems:
			print("Unplaced:", s)


	for s in spoiler.keys():
		s_value = spoiler[s]
		if s_value not in state or state[s_value].item == "SILVER_LEAF":
			print("Cannot reach:",s, s_value)



def removeWarpTrash(trashItems, criticalTrash, dontReplace, res_removed_items):
	if len(res_removed_items) > 0:
		unreplaced_items = []

		item_counter = {}
		for i in trashItems:
			if i not in item_counter:
				item_counter[i] = 0
			item_counter[i] += 1

		for ind in range(0, len(res_removed_items)):
			# TODO Add check to NOT remove critical trash or DO NOT REPLACE items
			# Unless you HAVE to
			remove = True
			while remove:
				remove = False
				if len(trashItems) > 0:

					# TODO Prioritse items that there are more of
					# Given that they are not in don't replace

					#inv_dict = {v: k for k, v in item_counter.items()}
					#max_value = max(inv_dict.keys())

					rm_index = random.randrange(0, len(trashItems))
					removing_item = trashItems[rm_index]
					trashItems.remove(removing_item)
					if removing_item in criticalTrash:
						remove = True
						unreplaced_items.append(removing_item)
					elif removing_item in dontReplace:
						remove = True
						unreplaced_items.append(removing_item)
				else:
					removed_item = unreplaced_items.pop()
		trashItems.extend(unreplaced_items)

	return trashItems

def randomizeRom(romPath, goal, seed, flags = [], patchList = [], banList = None, allowList = None, modifiers = [],
				 adjustTrainerLevels = False,adjustRegularWildLevels = False, adjustSpecialWildLevels = False, trainerLVBoost = 0,
				 wildLVBoost = 0,
				 requiredItems = ['Surf', 'Squirtbottle', 'Flash', 'Mystery Egg', 'Cut', 'Strength', 'Secret Potion','Red Scale', 'Whirlpool','Card Key', 'Basement Key', 'Waterfall', 'S S Ticket','Bicycle','Machine Part', 'Lost Item', 'Pass', 'Fly'],
				 plandoPlacements = {}, coreProgress= ['Surf','Fog Badge', 'Pass', 'S S Ticket', 'Squirtbottle','Cut','Hive Badge'],
				 otherSettings = {}, bonusTrash = [],hintConfig=None):
	#print('required items are')
	#print(requiredItems)

	requiredItemsCopy = copy.copy(requiredItems)
	changeListDict = defaultdict(lambda: [])
	extraTrash = []
	newItems = []
	maybeNewItems = []
	dontReplace = []
	addedProgressList = []
	for i in modifiers:
		#print(i)
		if 'FlagsSet' in i:
			flags.extend(i['FlagsSet'])
		if 'Changes' in i:
			for j in i['Changes']:
				changeListDict[j['Location']].append(j) 
		if 'AddedItems' in i:
			for j in i['AddedItems']:
				if j not in requiredItemsCopy:
					requiredItemsCopy.append(j)
					addedProgressList.append(j)
			#print(requiredItems)
		if 'AddedTrash' in i:
			extraTrash.extend(i['AddedTrash'])
		if 'NewGamePatches' in i:
			for j in i['NewGamePatches']:
				pfile = open(j)
				ptext = pfile.read()
				patchList.extend(json.loads(ptext))
		if 'NewItems' in i:
			newItems.extend(i['NewItems'])
		if 'MaybeNewItems' in i:
			maybeNewItems.extend(i['MaybeNewItems'])
		if 'DontReplace' in i:
			dontReplace.extend(i['DontReplace'])
	#print(changeListDict)
	badgeRandoCheck = not "BadgeItemShuffle" in otherSettings

	if "Warps" in flags:
		GenerateWarpData.interpretDataForRandomisedRom(romPath)

	if "Start With Bike" in flags:
		requiredItemsCopy.remove("Bicycle")

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
	Mineral.isTrash = badgeRandoCheck
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
		Thunder.isTrash = badgeRandoCheck
		Thunder.Name = 'Thunder Badge'
		Thunder.Code = 37
		Marsh = Badge.Badge()
		Marsh.isTrash = badgeRandoCheck
		Marsh.Name = 'Marsh Badge'
		Marsh.Code = 40
		Rainbow = Badge.Badge()
		Rainbow.isTrash = badgeRandoCheck
		Rainbow.Name = 'Rainbow Badge'
		Rainbow.Code = 38
		Soul = Badge.Badge()
		Soul.isTrash = badgeRandoCheck
		Soul.Name = 'Soul Badge'
		Soul.Code = 39
		Cascade = Badge.Badge()
		Cascade.isTrash = badgeRandoCheck
		Cascade.Name = 'Cascade Badge'
		Cascade.Code = 36
		Boulder = Badge.Badge()
		Boulder.isTrash = badgeRandoCheck
		Boulder.Name = 'Boulder Badge'
		Boulder.Code = 35
		Volcano = Badge.Badge()
		Volcano.isTrash = badgeRandoCheck
		Volcano.Name = 'Volcano Badge'
		Volcano.Code = 41
		Earth = Badge.Badge()
		Earth.isTrash = badgeRandoCheck
		Earth.Name = 'Earth Badge'
		Earth.Code = 42
		BadgeDict = {'Fog Badge':Fog, 'Zephyr Badge':Zephyr, 'Hive Badge':Hive, 'Plain Badge': Plain, 'Storm Badge': Storm, 'Mineral Badge': Mineral, 'Glacier Badge': Glacier, 'Rising Badge': Rising, 'Thunder Badge': Thunder, 'Marsh Badge' : Marsh, 'Rainbow Badge': Rainbow, 'Soul Badge': Soul, 'Cascade Badge': Cascade,'Boulder Badge': Boulder, 'Volcano Badge': Volcano, 'Earth Badge': Earth}
	else:
		BadgeDict = {'Fog Badge':Fog, 'Zephyr Badge':Zephyr, 'Hive Badge':Hive, 'Plain Badge': Plain, 'Storm Badge': Storm, 'Mineral Badge': Mineral, 'Glacier Badge': Glacier, 'Rising Badge': Rising}

	result = ['Nothing', 'Here']

	# Don't re-load data from folder on failure!
	fullLocationData = LoadLocationData.LoadDataFromFolder(".", banList, allowList, changeListDict, flags)

	seedIncrements = 0
	completeResult = False

	KEEP_GOING = False

	while goal not in result[0] or not completeResult:
		try:
			completeResult = True
			res_items = fullLocationData[1].copy()
			res_locations = fullLocationData[0].copy()
			res_removed_items = fullLocationData[2].copy()
			progressItems = copy.copy(requiredItemsCopy)
			#hardcoding key item lookups for now, pass as parameter in future
			keyItemMap = {'Surf':'HM_SURF', 'Squirtbottle':"SQUIRTBOTTLE", 'Flash':'HM_FLASH', 'Mystery Egg':'MYSTERY_EGG', 'Cut':'HM_CUT','Strength': 'HM_STRENGTH','Secret Potion':'SECRETPOTION', 'Red Scale':'RED_SCALE','Whirlpool': 'HM_WHIRLPOOL', 'Card Key': 'CARD_KEY', 'Basement Key':'BASEMENT_KEY', 'Waterfall':'HM_WATERFALL','S S Ticket':'S_S_TICKET', 'Machine Part': 'MACHINE_PART','Lost Item':'LOST_ITEM','Bicycle':'BICYCLE', 'Pass':'PASS','Fly':'HM_FLY', 'Clear Bell': 'CLEAR_BELL', 'Rainbow Wing':'RAINBOW_WING', 'Pokegear':'ENGINE_POKEGEAR','Radio Card':'ENGINE_RADIO_CARD','Expansion Card':'ENGINE_EXPN_CARD'}
			criticalTrash = ['ENGINE_POKEDEX', 'COIN_CASE', 'ITEMFINDER', 'SILVER_WING', 'OLD_ROD', 'GOOD_ROD', 'SUPER_ROD', 'BLUE_CARD']
			criticalTrash.extend(dontReplace)
			invKeyItemMap = defaultdict(lambda: '')
			for i in keyItemMap:
				invKeyItemMap[keyItemMap[i]] = i
			trashItems = sorted([x for x in res_items if not x in keyItemMap.values() or invKeyItemMap[x] not in progressItems]) #ensure progress items don't sneak into trash list
			trashItems.extend(sorted(extraTrash))
			trashItems = random.sample(trashItems, k=len(trashItems))

			# This is intended to remove warp trash to keep the item balance level
			# At first, I assumed this was the issue with items not being placed
			# This should be included for tidiniess, but leads to less roms being created
			# TODO Add a configuration to use this checker to remove some items from the possible trash pool
			if "Warps" in flags:
				trashItems = removeWarpTrash(trashItems, criticalTrash, dontReplace, res_removed_items)

			if 'BonusItems' in otherSettings or (len(newItems)+len(maybeNewItems)) > 0:
				if 'BonusItems' in otherSettings:
					bonusTrash = copy.copy(otherSettings['BonusItems'])
				else:
					bonusTrash = []
				bonusTrash.extend(copy.deepcopy(newItems))
				maybeAdd = []
				for i in maybeNewItems: #Change to only add MaybeNewItems if not or the ones added are likely duplicated
					if not i in bonusTrash and not i in trashItems:
						maybeAdd.append(i)
				bonusTrash.extend(maybeAdd)
				for i in range(0,len(trashItems)):
					if len(bonusTrash) > 0 and (not (trashItems[i] in criticalTrash)):
						trashItems[i] = bonusTrash.pop(0)
			#place bonus trash replacing non-critical trash
			if 'TrashItemList' in otherSettings:
				trashItems = copy.deepcopy(otherSettings['TrashItemList'])
				if "Warps" in flags:
					trashItems = removeWarpTrash(trashItems, criticalTrash, dontReplace, res_removed_items)
				if 'ProgressItems' in otherSettings:
					progressItems = copy.deepcopy(otherSettings['ProgressItems'])
					progressItems.extend(addedProgressList)
					#print(otherSettings)
					for i in progressItems:
						if i in trashItems:
							trashItems.remove(i)
			#print(progressItems)
			#print(trashItems)
			LocationList = res_locations
			rmCore = []
			#print(coreProgress)
			for i in coreProgress:
				if not i in progressItems:
					rmCore.append(i)
			for i in rmCore:
				coreProgress.remove(i)
			if(not "BadgeItemShuffle" in otherSettings):
				result = RandomizeItems.RandomizeItems('None',LocationList,progressItems,trashItems,BadgeDict, seed, inputFlags = flags, plandoPlacements = plandoPlacements, coreProgress = coreProgress)
			else:
				rBadgeList = []
				for i in BadgeDict:
					rBadgeList.append(i)
				result = RandomizeItemsBadges.RandomizeItems('None',LocationList,progressItems,trashItems,BadgeDict, seed, inputFlags = flags, reqBadges = rBadgeList, plandoPlacements = plandoPlacements, coreProgress = coreProgress, dontReplace = dontReplace)
			if goal not in result[0]:
				handleBadSpoiler(result, flags)
				print("bad run, retrying")
			elif len(result) > 6:
				remainingProgressItems = result[6]
				if len(remainingProgressItems) > 0:
					print("Successful seed, but not all items placed...")
					handleBadSpoiler(result, flags)
					print("bad run, retrying")
					completeResult = False
			if KEEP_GOING and goal in result[0]:
				print("Keep going...")
				completeResult = False
		except Exception as err:
			print('Failed with error: '+str(err)+' retrying...')
			completeResult = False
			traceback.print_exc()
		seed = seed+1
		seedIncrements += 1
	print('-------')

	print("Seed increments:",seedIncrements-1)




	for j in result[0]:
		i = result[0][j]
		if(i.NormalItem is None and i.isItem()):
			pass
			#print(i.Name)
	print('-------')
	for j in result[0]:
		i = result[0][j]
		if(i.NormalItem is not None and not i.isItem()):
			pass
			#print(i.Name)

	yamlfile = open("crystal-speedchoice-label-details.json",encoding='utf-8')
	yamltext = yamlfile.read()
	addressLists = json.loads(yamltext)
	addressData = {}
	for i in addressLists:
		addressData[i['label'].split(".")[-1]] = i
	#print(addressData)

	item_desc = open("ItemDescriptions.json")
	descs = item_desc.read()
	desc_addr = json.loads(descs)
	desc_addr_data = {}
	for i in desc_addr:
		desc_addr_data[i['name'].split(".")[-1]] = i

	sign_desc = open("Config/NewSignData.json")
	s_descs = sign_desc.read()
	sign_desc_addr = json.loads(s_descs)
	sign_addr_data = {}
	for i in sign_desc_addr:
		sign_addr_data[i['name'].split(".")[-1]] = i




	class PriorityObject:
		def __init__(self, name, types, keys):
			self.HintName = name
			self.HintTypes = types
			self.HintKeys = keys

	pri_file = open("Config/PriorityHints.json")
	p_d = pri_file.read()
	priority_data = json.loads(p_d)
	priority_list=[]
	for i in priority_data:
		hintTypes = i["HintTypes"] if "HintTypes" in i else []
		hintKeys = i["HintKeys"] if "HintKeys" in i else []
		#print("HINTKEYS:", hintTypes, hintKeys)
		item = PriorityObject(i["HintName"],hintTypes,hintKeys)
		priority_list.append(item)

	if hintConfig is not None and hintConfig.UseHints and hintConfig.BadgeIcon:
		badgeHintFontPatch = "Patches/BadgeSymbol.json"
		pfile = open(badgeHintFontPatch)
		ptext = pfile.read()
		patchList.extend(json.loads(ptext))

	maxDist = max(result[2].values())
	f = open(romPath,'r+b')
	romMap = mmap.mmap(f.fileno(),0)

	RandomizerRom.ApplyGamePatches(romMap, patchList)

	#newTree = PokemonRandomizer.randomizeTrainers(result[0],85,lambda y: monFun(y,1001,85),True,banMap)
	#get furthest item location distance

	RandomizerRom.DirectWriteItemLocations(result[0].values(), addressData,romMap,'Progressive Rods' in flags)
	if adjustRegularWildLevels:
		RandomizerRom.WriteWildLevelsToMemory(result[0], result[2],addressData,romMap,wildLVBoost,maxDist)
	if adjustSpecialWildLevels:
		RandomizerRom.WriteSpecialWildToMemory(result[0], result[2],addressData,romMap,wildLVBoost,maxDist)
	if adjustTrainerLevels:
		RandomizerRom.WriteTrainerDataToMemory(result[0],result[2],addressData,romMap,trainerLVBoost,maxDist)

	if hintConfig is not None and hintConfig.UseHints:
		hint_desc, locationList = RandomizeFunctions.GenerateHintMessages(result[1].copy(), result[4].copy(), res_locations,
															criticalTrash, BadgeDict, result[5].copy(), otherSettings,
															hintConfig, allowList, LocationList,
																		  flags, goal)

		RandomizeFunctions.removeRedundantHints(hint_desc, hintConfig, locationList)

		creation_data = RandomizeFunctions.PrepareHintMessages(sign_addr_data, hint_desc, priority_list, flags, hintConfig,
															   locationList)

		RandomizerRom.WriteDescriptionsToMemory(romMap, creation_data, hintConfig)
		if hintConfig.HideSigns:
			dead_hints = RandomizeFunctions.getHintsToRemove(creation_data, hintConfig)
			RandomizerRom.WriteHideUnusedSigns(romMap, dead_hints)



	if "SilverBadgeUnlockCount" in otherSettings:
		RandomizerRom.WriteOakBadgeCheckNumber(otherSettings["SilverBadgeUnlockCount"], addressData, romMap)
	#RandomizerRom.WriteTrainerLevels(result[0], result[2],newTree)
	#RandomizerRom.WriteWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
	#RandomizerRom.WriteSpecialWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
	#print(result[2])
	#print(result[1])
	return result
