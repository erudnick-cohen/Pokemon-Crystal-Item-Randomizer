import GenerateWarpData
import Items
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

import Static


def handleBadSpoiler(resultDict, flags, minSize=None, maxSize=None):
	spoiler = resultDict["Spoiler"]
	reachable = resultDict["Reachable"]

	if "Warps" in flags:
		# Debugging points to be aware of, due to bad warp rom at this time
		if "Victory Road Gate "+LoadLocationData.WARP_OPTION not in reachable:
			pass
		if "Oaks Lab "+LoadLocationData.WARP_OPTION not in reachable:
			pass

	if "ProgressList" in resultDict:
		remainingProgressItems = resultDict["ProgressList"]
		for s in remainingProgressItems:
			print("Unplaced:", s)


	prepared_commands = []

	for s in spoiler.keys():
		s_value = spoiler[s]
		if s_value not in reachable or reachable[s_value].item == "SILVER_LEAF":
			prepared_commands.append("Cannot reach:"+s+" "+s_value)

	if minSize is None and maxSize is None:
		print(prepared_commands)
	elif minSize is None and len(prepared_commands) < maxSize:
		print(prepared_commands)
	elif maxSize is None and len(prepared_commands) > minSize:
		print(prepared_commands)
	elif len(prepared_commands) < maxSize and len(prepared_commands) > minSize:
		print(prepared_commands)



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

			itemAtIndex = res_removed_items[ind]
			if not itemAtIndex.isItem() or itemAtIndex.Dummy:
				continue

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
						print("remove:", removing_item)
				else:
					removed_item = unreplaced_items.pop()

		trashItems.extend(unreplaced_items)

	return trashItems

def ProcessModifiers(modifiers, flags, inputVariables, changeListDict, requiredItemsCopy, addedProgressList, extraTrash, patchList,
					 newItems, maybeNewItems, maybeRemoveItems, dontReplace, disabledPatches):
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
		if 'MaybeRemoveItems' in i:
			maybeRemoveItems.extend(i["MaybeRemoveItems"])
		if 'DontReplace' in i:
			dontReplace.extend(i['DontReplace'])
		if 'VariablesSet' in i:
			for variableItem in i["VariablesSet"]:
				for variable in variableItem.keys():
					inputVariables[variable] = variableItem[variable]
		if 'DisablePatches' in i:
			for patch in i["DisablePatches"]:
				disabledPatches.append(patch)


class PriorityObject:
	def __init__(self, name, types, keys):
		self.HintName = name
		self.HintTypes = types
		self.HintKeys = keys


def CheckForE4Reachable(resultDict):
	E4Flag = True
	E4Found = ["Will", "Koga", "Bruno", "Karen", "Lance"]
	foundAll = True
	for mapReach in E4Found:
		if mapReach not in resultDict["Reachable"]:
			print("Not found:", mapReach)
			foundAll = False
			break
	if not foundAll:
		# TODO Add this as a warning display
		print("Successful seed, but cannot reach all E4...")
		E4Flag = False

	return E4Flag

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
	maybeRemoveItems = []
	disabledPatches = []
	inputVariables = {}

	yamlfile = open(Static.default_labels_file, encoding='utf-8')
	yamltext = yamlfile.read()
	addressLists = json.loads(yamltext)
	addressData = {}
	for i in addressLists:
		addressData[i['label'].split(".")[-1]] = i

	f = open(romPath, 'r+b')
	romMap = mmap.mmap(f.fileno(), 0)

	version_check = RandomizeFunctions.CheckVersion(addressData, romMap)
	if not version_check:
		return None

	ProcessModifiers(modifiers, flags, inputVariables, changeListDict, requiredItemsCopy, addedProgressList, extraTrash, patchList,
						 newItems, maybeNewItems, maybeRemoveItems, dontReplace, disabledPatches)

	if "Warps" in flags:
		mod_changes = GenerateWarpData.InterpretWarpChanges(romPath)

		ProcessModifiers(mod_changes, flags, inputVariables, changeListDict, requiredItemsCopy, addedProgressList, extraTrash, patchList,
						 newItems, maybeNewItems, maybeRemoveItems, dontReplace, disabledPatches)

	#print(changeListDict)
	badgeRandoCheck = not "BadgeItemShuffle" in otherSettings

	if "Warps" in flags:
		GenerateWarpData.interpretDataForRandomisedRom(romPath)

		#warpOutput = "Warp Data/warp-output.tsv"
		#warpTSVData = LoadLocationData.readTSVFile(warpOutput)

	for disablePatch in disabledPatches:
		removing = []
		for patch in patchList:
			if patch["description"] == disablePatch:
				removing.append(patch)

		for remove in removing:
			patchList.remove(remove)





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

	resultDict = {}

	# Don't re-load data from folder on failure!
	fullLocationData = LoadLocationData.LoadDataFromFolder(".", banList, allowList, changeListDict, flags)

	seedIncrements = 0
	completeResult = False

	# Debug code for finding odd behaviour
	#seed += 160

	spoilerLoop = False
	spoilerDetails = {}
	spoilerTotal = 200
	spoilerCount = 0

	if spoilerLoop:
		flat = LoadLocationData.FlattenLocationTree(fullLocationData[0])
		items = [ f.Name for f in flat if f.Type == "Item" or f.Type == "Gym" or f.Type == "Shop" or f.Type == "BargainShop" ]
		for item in items:
			spoilerDetails[item] = {}

	while ("Reachable" not in resultDict or goal not in resultDict["Reachable"]) or not completeResult or spoilerLoop:
		try:
			completeResult = True
			res_items = fullLocationData[1].copy()
			res_locations = fullLocationData[0].copy()
			res_removed_items = fullLocationData[2].copy()
			progressItems = copy.copy(requiredItemsCopy)
			#hardcoding key item lookups for now, pass as parameter in future
			keyItemMap = Items.GetKeyItemMap()
			criticalTrash = ['ENGINE_POKEDEX', 'COIN_CASE', 'ITEMFINDER', 'SILVER_WING', 'OLD_ROD', 'GOOD_ROD', 'SUPER_ROD', 'BLUE_CARD']
			criticalTrash.extend(dontReplace)
			invKeyItemMap = Items.getInverseKeyItemMap()

			# Some instances of progress items might have a duplicate, e.g. Escape Ropes
			# But only want those now added to progress items
			multiTrash = []
			oneInstanceOf = []
			multiInstancesOf = [ x for x in res_items if invKeyItemMap[x] in progressItems
								 and (len([x2 for x2 in res_items if x == x2]) > 1) ]

			for x in multiInstancesOf:
				if x not in oneInstanceOf:
					oneInstanceOf.append(x)
				else:
					multiTrash.append(x)

			trashItems = sorted([x for x in res_items if not x in keyItemMap.values() or invKeyItemMap[x] not in progressItems])
			trashItems.extend(sorted(multiTrash))
			#ensure progress items don't sneak into trash list

			trashItems.extend(sorted(extraTrash))
			trashItems = random.sample(trashItems, k=len(trashItems))

			itemsRemoved = 0

			for item in maybeRemoveItems:
				if item in trashItems:
					itemsRemoved += 1
					trashItems.remove(item)

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
					if len(bonusTrash) == 0:
						break
					if itemsRemoved > 0:
						itemsRemoved -= 1
						trashItems.append(bonusTrash.pop(0))
					elif len(bonusTrash) > 0 and (not (trashItems[i] in criticalTrash)):
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
			#if(not "BadgeItemShuffle" in otherSettings):
			#	resultDict = RandomizeItems.RandomizeItems('None',LocationList,progressItems,trashItems,BadgeDict, seed, inputFlags = flags, plandoPlacements = plandoPlacements, coreProgress = coreProgress)
			#else:
			# All the most recent logic now resides in ItemsBadges, so this one should be updated to support no BadgeItem Shuffle
			badgeShuffle = otherSettings["BadgeItemShuffle"] is None or otherSettings["BadgeItemShuffle"] if "BadgeItemShuffle" in otherSettings else False
			rBadgeList = []
			for i in BadgeDict:
				rBadgeList.append(i)
			#print(BadgeDict)
			resultDict = RandomizeItemsBadges.RandomizeItems('None',LocationList,progressItems,trashItems,BadgeDict, seed,
															 inputFlags = flags, inputVariables = inputVariables, reqBadges = rBadgeList, plandoPlacements = plandoPlacements,
															 coreProgress = coreProgress, dontReplace = dontReplace, badgeShuffle=badgeShuffle)

			if goal not in resultDict["Reachable"]:
				handleBadSpoiler(resultDict, flags, maxSize=10 if spoilerLoop else None)
				print("bad run, retrying")
			elif "ProgressList" in resultDict:
				print("Final checks...")
				completeResult = True


				remainingProgressItems = resultDict["ProgressList"]
				if len(remainingProgressItems) > 0:
					print("Successful seed, but not all items placed...")
					handleBadSpoiler(resultDict, flags)
					print("bad run, retrying")
					completeResult = False
				# Check for other requirements for FULL completion
				# This DOESN'T check possibility before Red however


				completeResult = completeResult and CheckForE4Reachable(resultDict)

				#reachableItems = [i.Name.replace(" ", "_") for i in resultDict["Reachable"].values()
				#				  if (i.isItem() or i.isGym()) and not i.Dummy]
				#reachableItems.sort()
				#print(reachableItems)


				if completeResult and spoilerLoop:

					for s in resultDict["Spoiler"].keys():
						s_value = resultDict["Spoiler"][s]
						if s not in spoilerDetails[s_value]:
							spoilerDetails[s_value][s] = 0

						spoilerDetails[s_value][s] += 1

					print("Spoiler loop::", spoilerCount, spoilerTotal)

					spoilerCount += 1
					if spoilerLoop and spoilerCount > spoilerTotal:
						spoilerLoop = False

						json_out = json.dumps(spoilerDetails, indent=2)
						print(json_out)

		except Exception as err:
			print('Failed with error: '+str(err)+' retrying...')
			completeResult = False
			traceback.print_exc()
		seed = seed+1
		seedIncrements += 1
	print('-------')

	print("Seed increments:",seedIncrements-1)

	for j in resultDict["Reachable"]:
		i = resultDict["Reachable"][j]
		if(i.NormalItem is None and i.isItem()):
			pass
			#print(i.Name)
	print('-------')
	for j in resultDict["Reachable"]:
		i = resultDict["Reachable"][j]
		if(i.NormalItem is not None and not i.isItem()):
			pass
			#print(i.Name)


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

	maxDist = max(resultDict["State"].values())


	RandomizerRom.ApplyGamePatches(romMap, patchList)

	#newTree = PokemonRandomizer.randomizeTrainers(result[0],85,lambda y: monFun(y,1001,85),True,banMap)
	#get furthest item location distance

	locations_list = resultDict["Reachable"].values()

	RandomizerRom.DirectWriteItemLocations(locations_list, addressData,romMap,'Progressive Rods' in flags)
	if adjustRegularWildLevels:
		RandomizerRom.WriteWildLevelsToMemory(locations_list, resultDict["State"],addressData,romMap,wildLVBoost,maxDist)
	if adjustSpecialWildLevels:
		RandomizerRom.WriteSpecialWildToMemory(locations_list, resultDict["State"],addressData,romMap,wildLVBoost,maxDist)
	if adjustTrainerLevels:
		RandomizerRom.WriteTrainerDataToMemory(locations_list,resultDict["State"],addressData,romMap,trainerLVBoost,maxDist)

	if "Price Randomisation" in flags:
		priceSettings = {
			"min_below": 0.5,
			"max_above": 2,
			"min_variance": 0,
			"keep_free": False,
			"shop_settings": {}
		}

		if "MinBelow" in inputVariables:
			priceSettings["min_below"] = inputVariables["MinBelow"]
		if "MaxAbove" in inputVariables:
			priceSettings["max_above"] = inputVariables["MaxAbove"]
		if "MinVariance" in inputVariables:
			priceSettings["min_variance"] = inputVariables["MinVariance"]
		if "KeepFree" in inputVariables:
			priceSettings["keep_free"] = inputVariables["KeepFree"]
		if "CherrygroveMaxPrice" in inputVariables:
			priceSettings["shop_settings"]["MartCherrygroveBetter"] = {
				"MaxPrice":	inputVariables["CherrygroveMaxPrice"]
			}

		#TODO: In future, make items in later marts more expensive if not present in earlier marts

		itemPrices = RandomizeFunctions.RandomizePrices(priceSettings, locations_list)
		RandomizerRom.WriteItemPricesToMemory(addressData, romMap, itemPrices)

		RandomizerRom.WriteHardCodedPricesToMemory(addressData, romMap, itemPrices, locations_list)

		# Handle hard-coded prices


	if hintConfig is not None and hintConfig.UseHints:
		hint_desc, locationList = RandomizeFunctions.GenerateHintMessages(resultDict["Spoiler"].copy(), resultDict["Trash"].copy(), res_locations,
															criticalTrash, BadgeDict, resultDict["Dependencies"].copy(), otherSettings,
															hintConfig, allowList, LocationList, flags, goal)

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
	return resultDict
