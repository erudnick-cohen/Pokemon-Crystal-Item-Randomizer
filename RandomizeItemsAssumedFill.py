import LoadLocationData
from collections import defaultdict
import random
import copy
import time

def RandomizeItems(goalID,locationTree, progressItems, trashItems, badgeData, inputFlags=[], reqBadges = { 'Zephyr Badge', 'Fog Badge', 'Hive Badge', 'Plain Badge', 'Storm Badge', 'Glacier Badge', 'Rising Badge'}, coreProgress= ['Surf','Fog Badge', 'Pass', 'S S Ticket', 'Squirtbottle','Cut','Hive Badge'], allPossibleFlags = ['Johto Mode','Kanto Mode']):
	#build progress set
	progressList = copy.copy(progressItems)
	progressList.extend(reqBadges)
	progressSet = copy.copy(progressList)
	coreProgress = list(set(coreProgress).intersection(set(progressSet)))
	locList = LoadLocationData.FlattenLocationTree(locationTree)
	allocatedList = []

	#define set of badges
	badgeSet = list(badgeData.keys())
	#define set of trash badges
	trashBadges = list(set(badgeData.keys()).difference(set(reqBadges)))
	#stores current requirements for each location
	requirementsDict = defaultdict(lambda: [])

	#shuffle the lists (no seriously, this is a perfectly valid randomization strategy)
	random.shuffle(locList)
	random.shuffle(progressList)
	random.shuffle(coreProgress)
	random.shuffle(trashItems)
	#build spoiler
	spoiler = {}
	#print('Building mappings')
	#note: these are the randomizer only flags, they do not map to actual logic defined in the config files
	#flagList = ['Rocket Invasion', '8 Badges', 'All Badges']
	flagList = ['Assumed Fill', 'All Badges']
	#build the initial requirements mappings
	allReqsList = copy.copy(progressSet)
	itemCount = 0
	for i in locList:
		#baseline requirements
		#allReqs = i.LocationReqs+i.FlagReqs+i.itemReqs
		allReqs = i.requirementsNeeded(defaultdict(lambda: False))
		allReqsList.extend(allReqs) 
		allReqsList.append(i.Name)
		requirementsDict[i.Name].append(allReqs)
		for j in i.FlagsSet:
			requirementsDict[j].append(allReqs)
			flagList.append(j)
		if i.Type == 'Item':
			itemCount = itemCount+1
	print('Total number of items: '+str(itemCount))
	#extract all core items out and put them in shuffled order at the start (which is the BACK) of the item list
	#this is done because these items unlock way too many item locations, so we want to maximize their legal locations
	for i in coreProgress:
		progressList.remove(i)
	progressList = progressList+coreProgress
	#print(progressList)
	
	#keep copy of initial requirements dictionary to check tautologies
	initReqDict = copy.copy(requirementsDict)
	usedFlagsList = list(set(allReqsList).intersection(allPossibleFlags))
	#begin assumed fill loop
	valid = True
	while(len(progressList)>0 and valid):
		#pick and item to place
		toAllocate = progressList.pop()
		#print('Allocating '+toAllocate)
		if toAllocate in progressItems:
			allocationType = 'Item'
		else:
			allocationType = 'Gym'
		#iterate through randomly ordered locations until a feasible location to place item is found
		valid = False
		iter = 0
		retryPasses = 4
		while not valid and iter < len(locList) and retryPasses > 0:
			legal = True
			#is it the right type of location?
			#print(locList[iter].Name)
			#print(locList[iter].Type)
			if(locList[iter].Type == allocationType):
				#print('Trying '+locList[iter].Name)
				#do any of its dependencies depend on this item/badge?
				randOpt = random.choice(range(0,len(requirementsDict[locList[iter].Name])))
				allDepsList = copy.copy(requirementsDict[locList[iter].Name][randOpt])
				oldDepsList = []
				newDeps = allDepsList
				addedList = [locList[iter].Name]
				revReqDict = defaultdict(lambda: [])
				while oldDepsList != allDepsList and legal:
					oldDepsList = allDepsList
					for j in newDeps:
						jReqs = []
						if(len(requirementsDict[j])>0):
							#print('Choosing non-tautological path for '+j)
							#choose a random path through dependencies that IS NOT A TAUTOLOGY!
							paths = copy.copy(requirementsDict[j])
							random.shuffle(paths)
							#pick an option from paths which isn't a tautology!
							tautologyCheck = True
							tautIter = 0
							#only need to pick if there are two options!
							if(len(requirementsDict[j])>1):
								#better strategy, if you choose option A from the multiple options, then the locations required by A CANNOT require j!
								#so when choosing a path to the locations required by A, we CANNOT choose an option with j as a dependency!
								#also, we don't pick paths that require the item we're trying to allocate, for obvious reasons
								trueOption = None
								for k in paths:
									#print('trying potential path:')
									#print(k)
									kTrue = True
									for l in k:
										kTrue = kTrue and (l not in revReqDict[j]) and toAllocate not in k
										lTrueOr = len(requirementsDict[l]) == 0
										for m in requirementsDict[l]:
											lTrueOr = lTrueOr or toAllocate not in m
										kTrue = kTrue and lTrueOr
										if not lTrueOr:
											1+1
											#print('False because '+l+' requires:')
											#print(requirementsDict[l])
										#if a flag we don't have is needed, we can't use that path
										kTrue = kTrue and not (l in usedFlagsList and l not in inputFlags)
										if (l in usedFlagsList and l not in inputFlags):
											1+1
											#print('False because the needed flag '+ l +' is not set')
											#print(usedFlagsList)
											#print(inputFlags)
									if(kTrue):
										trueOption = k
										#print('found non-tautological path')
										#print(k)
										break
									else:
										1+1
										#print('Path is false')
								#if new choice is none, ignore it because this is a true tautology
								#e.g. trying to place the squirtbottle at the sudowoodo junction
								if(not trueOption is None):
									#add all reverse dependencies onto new choice
									for k in trueOption:
										revReqDict[k].extend(revReqDict[j])
										revReqDict[k].append(j)
									jReqs = trueOption
									addedList.append(j)
									if len(paths)>1:
										1+1
										#print(revReqDict)
								else:
									legal = False
									#this is not a legal item location! because it involves a tautology!
									#print('Illegal tautology:')
									#print(paths)
									#print('The following could create the tautology when allocating '+ toAllocate +' to '+locList[iter].Name+':')
									#print(revReqDict[j])
							else:
								jReqs = requirementsDict[j][0]
								#print('found non-tautological path')
								#print(jReqs)
								addedList.append(j)
						for k in jReqs:
							if k not in allDepsList:
								newDeps.append(k)
					allDepsList.extend(newDeps)
					#print('Expanded dependencies of '+locList[iter].Name+' to:')
					#print(allDepsList)
					newDeps = []
				#if a dependency requires an input flag (not set by a location, a location, or a progress item), that flag MUST be set
				#print(allDepsList)
				#print(legal)
				#print(set(allDepsList).intersection(set(usedFlagsList)).issubset(inputFlags))
				#print(usedFlagsList)
				#print(set(allDepsList).intersection(set(usedFlagsList)))
				legal = legal and set(allDepsList).intersection(set(usedFlagsList)).issubset(inputFlags)
				if(not set(allDepsList).intersection(set(usedFlagsList)).issubset(inputFlags)):
					1+1
					#print(locList[iter].Name + ' is not legal because it needs flags that are not set')
					#print(set(allDepsList).intersection(set(usedFlagsList)))
				if(toAllocate not in allDepsList and legal):
					loc = locList.pop(iter)
					valid = True
					#print('Gave '+ toAllocate +' to '+ loc.Name)
					if(loc.isItem()):
						loc.item = toAllocate
						spoiler[loc.item] = loc.Name
					if(loc.isGym()):
						loc.badge = badgeData[toAllocate]
						badgeSet.remove(toAllocate)
						spoiler[loc.badge.Name] = loc.Name
					allocatedList.append(loc)
					#requirementsDict[toAllocate] = requirementsDict[loc.Name]
					requirementsDict[toAllocate] = [list(set(allDepsList))]
					#print(spoiler)
				else:
					#print(locList[iter].Name+' cannot contain '+toAllocate)
					if(toAllocate in allDepsList):
						1+1
						#print('...because it requires '+toAllocate+' to be reached in the first place!')
						#print(spoiler)
					else:
						1+1
						#print('...because its currently an illegal location')
						#print(spoiler)
					iter = iter+1
			else:
				iter = iter+1
			if iter == len(locList) and not valid:
				iter = 0
				retryPasses = retryPasses-1
				#print('retrying with different paths')

	#print('----')

	#traverse seed to both confirm beatability, allocate "trash" items and determine location distances
	#define the set of active initial locations to consider
	rodList = ['OLD_ROD','GOOD_ROD','SUPER_ROD']
	#overwrite rods into semi-progressive order
	if('SemiProgressiveRods' in inputFlags):
		#print(trashItems)
		for i in range(0,len(trashItems)):
			if('ROD' in trashItems[i]):
				trashItems[i] = rodList.pop()
		#print('---')
		#print(trashItems)
	activeLoc = copy.copy(locationTree)
	goalReached = False
	randomizerFailed = False
	#Initially we have no badges
	nBadges = 0
	#define the dict of currently accesible locations
	reachable = {}
	#define max distance of each badge
	maxBadgeDist = 0
	state = defaultdict(lambda: False)
	#set initial flags
	for i in inputFlags:
		state[i] = True
	#define mapping of state to distances at which parts of state were met
	stateDist = defaultdict(lambda: 0)
	stuckCount = 0
	while not goalReached and not randomizerFailed:
		#track if we're stuck
		stuck = True
		#shuffle the list of active locations to prevent any possible biases	
		random.shuffle(activeLoc)
		for i in activeLoc:
			#can we get to this location?
			if(i.isReachable(state) and i.Name not in reachable):
				#print(i.Name)
				#if we can get somewhere, we aren't stuck
				stuck = False
				#we can get somehwhere, so set this location in the state as true
				state[i.Name] = True
				#Add sublocations to the set of active locations
				activeLoc.extend(i.Sublocations)
				#set this location as reachable
				reachable[i.Name] = i
				activeLoc.remove(i)
				#set distance of this location
				maxdist = max([stateDist[x] for x in i.requirementsNeeded(defaultdict(lambda: False))],default = 0)
				if i.HasPKMN:
					maxdist = maxdist+1
				i.distance = maxdist
				#set distance of location
				stateDist[i.Name] = i.distance
				#set all relevant flags this location sets
				for j in i.getFlagList():
					state[j] = True
					stateDist[j] = i.distance
				#perform appropriate behaviors for location
				#if its an item, put an item in it
				if(i.isItem()):
					if(i.item is None):
						i.item = trashItems.pop()
						#print('Placing '+i.item +' in '+i.Name)
					else:
						state[i.item] = True
						stateDist[i.item] = max(stateDist[i.item],stateDist[i.Name])
				if(i.isGym()):
					maxBadgeDist = max(maxBadgeDist,i.distance)
					nBadges = nBadges+1
					if(i.badge is None):
						i.badge = badgeData[trashBadges.pop()]
					else:
						state[i.badge.Name] = True
						stateDist[i.badge.Name] = max(stateDist[i.badge.Name],stateDist[i.Name])
					#set badge count based flags
					if(nBadges == 7):
						state['Rocket Invasion'] = True
						stateDist['Rocket Invasion'] = maxBadgeDist
					if(nBadges == 8):
						state['8 Badges'] = True
						stateDist['8 Badges'] = maxBadgeDist
					if(nBadges == 16):
						state['All Badges'] = True
						stateDist['All Badges'] = maxBadgeDist
		if(stuckCount == 4):
			randomizerFailed = True
			for j in activeLoc:
				if(not state[j.Name]):
					1+1
					#print('Stuck on '+j.Name+', which needs:')
					#print(j.requirementsNeeded(state))
			#print(state)
		#check if we've become stuck
		if(stuck):
			stuckCount = stuckCount+1
		else:
			stuckCount = 0

	#print(stateDist)
	#print(spoiler)
	#print(nBadges)
	#print('illegal')
	#print('remaining')
	#print(trashItems)
	return (reachable, spoiler, stateDist, randomizerFailed)