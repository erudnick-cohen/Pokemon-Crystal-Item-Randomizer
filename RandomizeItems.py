from collections import defaultdict
from itertools import accumulate
import copy
import random

#goalID is the name of the goal of our search
#location tree is the list of locations(they are all trees)
#progressItems is the list of items that progress logic
#trashItems is everything else
#badgeData is a dict where the keys are the bagde names and the values are the badge objects
def RandomizeItems(goalID,locationTree, progressItems, trashItems, badgeData, inputFlags=None):
	if inputFlags is None:
		inputFlags = []
	#define state dict that determines if things are available or not
	state = defaultdict(lambda: False)
	#set initial flags
	for i in inputFlags:
		state[i] = True
	#define mapping of state to distances at which parts of state were met
	stateDist = defaultdict(lambda: 0)
	#define the spoiler dict
	spoiler = {}
	#Initially we have no badges
	nBadges = 0
	#define set of badges
	badgeSet = list(badgeData.keys())
	#define list of locations we put trash in
	trashSpots = []
	#define list of gyms we have reached that don't currently unlock anything
	trashGyms = []
	#define the dict of currently accesible locations
	reachable = {}
	#define the set of active initial locations to consider
	activeLoc = copy.copy(locationTree)
	#define max distance of each badge
	maxBadgeDist = 0
	#define paranoia variable for if the search screws up and ACTUALLY gets stuck
	stuckCount = 0
	
	oldTrashList = []
	allTrashList = []
	allTrashGyms = []
	newTrashGyms = []
	newSpots = []
	reqItems = copy.copy(progressItems)
	#this is hardcoded to crystal, remember you have to change this when you migrate this stuff to the ruby item randomizer
	reqBadges = { 'Zephyr Badge', 'Fog Badge', 'Hive Badge', 'Plain Badge', 'Storm Badge', 'Glacier Badge', 'Rising Badge'}
	#begin search and assignment
	goalReached = False
	randomizerFailed = False
	while not goalReached and not randomizerFailed:
		#print('Solution is')
		#print(spoiler)
		#track if we're stuck
		stuck = True
		#shuffle the list of active locations to prevent any possible biases	
		random.shuffle(activeLoc)
		#update the list of reachable locations and sublocations
		for i in activeLoc:
			#can we get to this location?
			if(i.isReachable(state) and i.Name not in reachable):
				#print(i.Name)
				#if we can get somewhere, we aren't stuck
				stuck = False
				stuckCount = 0
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
					#print('Storing Item:')
					#determine what item to put in
					#print(trashItems)
					#print(progressItems)
					itemType = random.choices(population = ['Trash', 'Progress'], weights = [len(trashItems), len(progressItems)])
					#print('Type is '+itemType[0]+' it is...')
					if(itemType[0] == 'Trash'):
						item = random.choice(trashItems)
						trashItems.remove(item)
						i.item = item
						trashSpots.append(i)
						newSpots.append(i)
					if(itemType[0] == 'Progress'):
						item = random.choice(progressItems)
						progressItems.remove(item)
						i.item = item
						#set the flag for this item
						state[item] = True
						stateDist[item] = i.distance
						spoiler[item] = i.Name
						newSpots.append(i)
					#print(i.item)
				#if its a gym, put a badge in it
				if(i.isGym()):
					#pick a random badge that hasn't been used yet
					badge = random.choice(badgeSet)
					badgeSet.remove(badge)
					i.badge = badgeData[badge]
					#if badge is trash, put gym in trash gym list
					if(badgeData[badge].isTrash):
						trashGyms.append(i)
						newTrashGyms.append(i)
					else:
						#otherwise add this badge to the state
						state[badge] = True
						stateDist[badge] = i.distance
						spoiler[badge] = i.Name
						newTrashGyms.append(i)
					nBadges = nBadges+1
					maxBadgeDist = max(maxBadgeDist,i.distance)
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
		#check if we've become stuck
		if(stuck):
			stuckCount = stuckCount+1
		else:
			stuckCount = 0
		if(stuckCount > 2):
			#update trashList
			random.shuffle(trashSpots)
			random.shuffle(newSpots)
			oldTrashList.extend(trashSpots)
			allTrashList.extend(newSpots)
			
			random.shuffle(newTrashGyms)
			allTrashGyms.extend(newTrashGyms)
			newTrashGyms = []
			newSpots = []

			#print(trashSpots)
			trashSpots = []
			#print('Got stuck, forcing progress')
			#print('Current state')
			#print(stateDist)
			#print(spoiler)
			stuckCount = stuckCount+1
			#Define set of possible locations to open up
			pLocations = copy.copy(activeLoc)
			#Filter set of feasible combindations of flags to remove impossible options
			removeElts = []
			for j in pLocations:
				#places with no requirements are places already visited, so ignore them
				if(j.Name not in stateDist):
					#print('Trying '+j.Name+', which needs:')
					#print(j.requirementsNeeded(state))
					#We need to check for not having enough badges and flags that aren't badges
					#Count number of reqs which are badges
					#also count reqs which aren't items
					itemCount = 0
					rBadgeCount = 0
					for k in j.requirementsNeeded(state):
						if(k in badgeData):
							rBadgeCount = rBadgeCount+1
						if(k in progressItems):
							itemCount = itemCount+1
					#if there are more flags than badge flags or not enough badge flags, we can't use this
					if(rBadgeCount>len(trashGyms) or itemCount+rBadgeCount != len(j.requirementsNeeded(state))):
						removeElts.append(j)
				else:
					removeElts.append(j)
			#remove these infeasible locations
			for j in removeElts:
				pLocations.remove(j)
			#Build list of feasible combinations of requirements
			reqSet = list(frozenset([frozenset(x.requirementsNeeded(state)) for x in pLocations]))
			#print("Resolvers are currently")
			#print(reqSet)
			if(len(reqSet)>0):
				#Determine appropriate weights for each requirement combinations
				weightList = [0]*len(reqSet)
				#note that each element will compare against itself once so all elements get at least a weight of 1
				for j in range(0,len(reqSet)):
					for k in range(0,len(reqSet)):
						if(reqSet[j]<=reqSet[k]):
							weightList[j] = weightList[j]+1
				#Invert all terms in weight list, this correctly adjusts the scaling of the problem
				#Scaling requires that if a requirment combination belongs to several sets, its total probability should be one
				#Thus if a requirement combination is a super set of an existing one, it should be less likely
				for j in range(0,len(weightList)):
					weightList[j] = 1/weightList[j]
				#Now choose the set of requirements that we need to fulfill randomly according to the weights
				reqs = random.choices(population = reqSet, weights = weightList)
				#For each requirement, make it so that it is met
				#print('Resolving issue with')
				#print(reqs[0])
				for j in reqs[0]:
					#if the requirement isn't a badge, its an item
					if(j not in badgeData):
						#Its an item, so find it in the progress items list
						#item = next(x for x in progressItems if x == j)
						progressItems.remove(j)
						
						#compute item density map, items are weighted based off distance from total number of items and weighted to not be clumped
						#compute item density map in the forwards direction
						itemDensityMap = [0]*len(oldTrashList)
						#initialize distance to large number so we get early areas the right weight
						itemDistSum = 1000
						iter = 0
						nProgressCount = 0
						for k in range(0,len(allTrashList)):
							#print('a '+str(k)+' b '+str(iter))
							if(allTrashList[k].item in reqItems):
								nProgressCount = nProgressCount+1
								itemDistSum = nProgressCount
							else:
								itemDensityMap[iter] = itemDistSum
								itemDistSum = itemDistSum+1
								iter = iter+1
						#print(itemDensityMap)
						#compute item density map in the reverse direction
						itemDistSum = nProgressCount
						iter = len(oldTrashList)-1
						rFlag = 0
						for k in range(len(allTrashList)-1,-1,-1):
							#print(k)
							#print(reqItems)
							if(allTrashList[k].item in reqItems):
								nProgressCount = nProgressCount-1
								itemDistSum = nProgressCount
								rFlag = 1
							else:
								if(rFlag == 1):
									itemDensityMap[iter] = min(itemDistSum,itemDensityMap[iter])
								itemDistSum = itemDistSum+1
								iter = iter-1
						#Pick a random location with trash and put the item there
						#This choice is biased to space out items to be evenly distributed
						dSum = sum(itemDensityMap)
						#print(itemDensityMap)
						randVal = random.uniform(0,dSum)
						randSpot = 0
						while(randVal>0):
							randVal = randVal-itemDensityMap[randSpot]
							randSpot = randSpot+1
						randSpot = randSpot-1
						#print(randSpot)
						#However, the mode is still randomized uniformly, so the main effect is a center-ish bias
						#randspot = int(round(random.triangular(1,len(oldTrashList)-1, random.randrange(1,len(oldTrashList)-1))))
						#place = random.choice(oldTrashList[randspot:])
						#the width of the triangular distribution used is based off the number of possible requirements that could be used as a resolver
						#this width is based off the ratio of the number of possible resolvers to the number of key items left, max 1
						#the ratio is multiplied by the number of inaccesible locations current present
						# center = random.triangular(1,len(oldTrashList),len(oldTrashList)/2);
						# rrange = len(oldTrashList)/2
						# if(2*len(pLocations)<len(oldTrashList)):
							# center = random.randrange(len(pLocations),len(oldTrashList)-len(pLocations))
							# rrange = len(pLocations)*min(1,len(reqSet)/max(1,len(progressItems)))
						# upper = min(len(oldTrashList)-1,center+rrange)
						# lower = max(center-rrange,1)
						# randspot = int(round(random.triangular(lower,upper,center)))
						#print(oldTrashList)
						if(len(oldTrashList)> 1 and rFlag == 1):
							#place = random.choice(oldTrashList[randspot:])
							place = oldTrashList[randSpot]
						elif(len(oldTrashList)> 1 and rFlag == 0):
							#place = random.choice(oldTrashList)
							place = oldTrashList[randSpot]
						else:
							place = oldTrashList[0]
						trashItems.append(place.item)
						place.item = j
						oldTrashList.remove(place)
						state[j] = True
						stateDist[j] = place.distance
						spoiler[j] = place.Name
					else:
						#print('badging')
						#print(allTrashGyms)
						#print(trashGyms)
						#print(reqItems)
						#It is a badge, pick a random trash gym and put it there
						#compute badge density map, items are weighted based off distance from total number of items and weighted to not be clumped
						#compute badge density map in the forwards direction
						badgeDensityMap = [0]*len(trashGyms)
						#initialize distance to large number so we get early areas the right weight
						itemDistSum = 1000
						iter = 0
						nProgressCount = 0
						for k in range(0,len(allTrashGyms)):
							#print('a '+str(k)+' b '+str(iter))
							#print(allTrashGyms[k].badge.Name)
							if(allTrashGyms[k].badge.Name in reqBadges):
								nProgressCount = nProgressCount+1
								itemDistSum = nProgressCount
							else:
								badgeDensityMap[iter] = itemDistSum
								itemDistSum = itemDistSum+1
								iter = iter+1
						#print(itemDensityMap)
						#compute item density map in the reverse direction
						#print('rev')
						itemDistSum = nProgressCount
						iter = len(trashGyms)-1
						rFlag = 0
						for k in range(len(allTrashGyms)-1,-1,-1):
							#print(k)
							#print(reqItems)
							if(allTrashGyms[k].badge.Name in reqBadges):
								nProgressCount = nProgressCount-1
								itemDistSum = nProgressCount
								rFlag = 1
							else:
								if(rFlag == 1):
									badgeDensityMap[iter] = min(itemDistSum,badgeDensityMap[iter])
								itemDistSum = itemDistSum+1
								iter = iter-1
						#Pick a random location with trash and put the item there
						#This choice is biased to space out items to be evenly distributed
						dSum = sum(badgeDensityMap)
						#print(badgeDensityMap)
						#print(stateDist)
						#print(spoiler)
						#print(reqs)
						#print(allTrashGyms)
						#print(rFlag)
						randVal = random.uniform(0,dSum)
						randSpot = 0
						while(randVal>0):
							randVal = randVal-badgeDensityMap[randSpot]
							randSpot = randSpot+1
						randSpot = randSpot-1
						
						
						#gym = random.choice(trashGyms)
						if(rFlag == 1):
							gym = trashGyms[randSpot]
						else:
							gym = random.choice(trashGyms)
						trashGyms.remove(gym)
						badgeSet.append(gym.badge.Name)
						badgeSet.remove(j)
						gym.badge = badgeData[j]
						state[j] = True
						stateDist[j] = gym.distance
						spoiler[j] = gym.Name
						#print('done')
			else:
				randomizerFailed = True
				#print("No Resolvers Available, randomizer has failed")
	#return the information we need
	#1 location dictionary of allocated locations
	#2 spoiler
	#3 stateDist
	#4 if we failed or not
	return (reachable, spoiler, stateDist, randomizerFailed)

