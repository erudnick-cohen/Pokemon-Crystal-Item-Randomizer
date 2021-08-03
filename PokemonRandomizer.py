import csv
from collections import defaultdict
import random
import yaml
import copy

#returns a function to randomly generate pokemon
def generateRandomMonFun(stateDist,locations):
	#first we loop through the set of various locations
	#so that we know the min requirements for the important moves
	moveDict = {}
	moveDict['Strength'] = 1000
	moveDict['Surf'] = 1000
	moveDict['Whirlpool'] = 1000
	moveDict['Waterfall'] = 1000
	moveDict['Cut'] = 1000
	moveDict['Flash'] = 1000
	moveDict['Rock Smash'] = 1000
	for i in stateDist:
		for j in moveDict:
			if(i in locations):
				if j in locations[i].requirementsNeeded(defaultdict(lambda: False)):
					moveDict[j] = min(moveDict[j],stateDist[j])
	
	#next we load in the learnset database
	monMove = defaultdict(lambda: [])
	bstMap = {}
	csvMap = {}
	csvMap['Flash'] = 3
	csvMap['Cut'] = 4
	csvMap['Strength'] = 5
	csvMap['Surf'] = 6
	csvMap['Whirlpool'] = 7
	csvMap['Waterfall'] = 8
	csvMap['Rock Smash'] = 9
	with open('pokedex.csv', newline='') as csvfile:
		reader = csv.reader(csvfile)
		for i in reader:
			for j in moveDict:
				if(i[csvMap[j]] == 'Yes'):
					monMove[j].append(str(i[1].upper()))
			bstMap[i[1].upper()] = int(i[2])
	#create function for providing a random feasible pokemon
	def monLookupFun(original,dist,range):
		bst = bstMap[original]
		monlist = list(bstMap.keys())
		random.shuffle(monlist)
		reqList = []
		#build list of required moves for this distance and mon
		for i in moveDict:
			if dist<moveDict[i] and original in monMove[i]:
				reqList.append(i)
		ok = False
		iter = 0
		mon = "INVALID"
		while not ok:
			mon = monlist[iter]
			ok = True
			if abs(bstMap[mon]-bst) <= range:
				for i in reqList:
					if mon not in monMove[i]:
						ok = False
			else:
				ok = False
			iter = iter + 1
		return mon
	return monLookupFun
	
#returns a randomized dictionary of the trainer data, with a specified range for base stat variation
#the randomized entries are put in a new entry in the dict called newCode
#banMap is a dict mapping specific trainers that cannot have other trainers pokemon, primarily for early gym leaders and lance
def randomizeTrainers(locations, bstrange,monFun,rivalFix = False,banMap = defaultdict(lambda: [])):
	#if the users specifies it, the rival will be homogenized
	#across one of his three possibilities per encounter
	#this prevents him from polluting the shuffle pool
	skipList = []
	tmapdict = {}
	if(rivalFix):
		rsets = []
		rsets.append(['RIVAL1 7','RIVAL1 8','RIVAL1 9'])
		rsets.append(['RIVAL1 10','RIVAL1 11','RIVAL1 12'])
		rsets.append(['RIVAL1 13','RIVAL1 14','RIVAL1 15'])
		rsets.append(['RIVAL2 1','RIVAL2 2','RIVAL2 3'])
		for i in rsets:
			random.shuffle(i)
			tmapdict[i[1]] = i[0]
			tmapdict[i[2]] = i[0]
			skipList.append(i[1])
			skipList.append(i[2])
	else:
		tmapfun = lambda x: x
	#build list of reachable trainers
	trainerList = []
	for i in locations:
		if locations[i].Trainers is not None:
			for j in locations[i].Trainers:
				trainerList.append(j)
	bstMap = {}
	#load in base stat information
	with open('pokedex.csv', newline='') as csvfile:
		reader = csv.reader(csvfile)
		for i in reader:
			bstMap[i[1].upper()] = int(i[2])
	#load up the trainer data
	yamlfile = open("TrainerData/Trainers.yaml")
	yamltext = yamlfile.read()
	trainerData = yaml.load(yamltext, Loader=yaml.FullLoader)
	
	#for trainers who don't have moves, randomizing the trainer file is just randomizing pokemon
	#for trainers who DO have moves, we SHUFFLE their pokemon with those of other trainers with moves
	mList = []
	for i in trainerData:
		if(i in trainerList and i not in skipList):
			if(trainerData[i]['Type'] == '1'):
				for j in range(0,len(trainerData[i]["Pokemon"])):
					mList.append((i,j,bstMap[trainerData[i]["Pokemon"][j]["Pokemon"]]))
			else:
				for q in range(0,len(trainerData[i]['Pokemon'])):
					k = trainerData[i]['Pokemon'][q]
					newcode = k['Code']
					pokemon = monFun(k['Pokemon'])
					level = k['Level']
					newlevel = level
					newcode = newcode.replace("db "+str(level)+", "+k['Pokemon'],"db "+str(newlevel)+", "+pokemon)
					trainerData[i]['Pokemon'][q]['NewCode'] = newcode
	#find a viable shuffle of the pokemon with moves
	shuffleDict = {}
	monList = copy.copy(mList)
	random.shuffle(monList)
	random.shuffle(mList)
	stuckList = []
	notStuck = []
	for i in mList:
		shuffleDict[i] = None
		for j in monList:
			if(abs(i[2]-j[2]) < bstrange and j[0] not in banMap[i[0]]):
				shuffleDict[i] = j
				monList.remove(j)
				notStuck.append(j)
				break
		else:
			stuckList.append(i)
	#for some reason this is needed
	for i in shuffleDict:
		if shuffleDict[i] is None and i in notStuck:
			notStuck.remove(i)
			if i not in stuckList:
				stuckList.append(i)
	#perform feasible swaps with things in the stuck list to fix everything
	while(len(stuckList)>0):
		print(stuckList)
		random.shuffle(notStuck)
		for i in stuckList:
			for j in notStuck:
				print(j)
				if(abs(j[2]-i[2]) < bstrange):
					if(abs(shuffleDict[j][2]-i[2]) < bstrange and j[0] not in banMap[i[0]]):
						#perform swap
						print('swap')
						print(i)
						print(j)
						old = shuffleDict[j]
						shuffleDict[j] = i
						shuffleDict[i] = old
						notStuck.append(i)
						stuckList.remove(i)
						break
					# else:
						# #can't swap, so put the old thing into the list of things that are stuck
						# old = shuffleDict[j]
						# shuffleDict[j] = i
						# stuckList.append(old)
						# #notStuck.remove(old)
						# stuckList.remove(i)
						# notStuck.append(i)
						# random.shuffle(notStuck)
						# print('swap')
						# print(i)
						# print(j)
						# break

	#finally, rewrite code for each entry
	for i in mList:
		print(str(i) +' has '+ str(shuffleDict[i]))
		basemon = trainerData[i[0]]["Pokemon"][i[1]]["Code"]
		newMon = trainerData[shuffleDict[i][0]]["Pokemon"][shuffleDict[i][1]]["Code"]
		#change level of new mon to match what the original was
		newMon = newMon.replace("db "+str(trainerData[shuffleDict[i][0]]["Pokemon"][shuffleDict[i][1]]["Level"]), "db "+ str(trainerData[i[0]]["Pokemon"][i[1]]["Level"]))
		trainerData[i[0]]["Pokemon"][i[1]]["NewCode"] = newMon
	
	#if we have any remappped trainers like the rival, update their entries
	for i in tmapdict:
		for q in range(0,len(trainerData[i]['Pokemon'])):
			trainerData[i]['Pokemon'][q]["Pokemon"] = trainerData[tmapdict[i]]['Pokemon'][q]["Pokemon"]
			trainerData[i]['Pokemon'][q]["Level"] = trainerData[tmapdict[i]]['Pokemon'][q]["Level"]
			trainerData[i]['Pokemon'][q]["Item"] = trainerData[tmapdict[i]]['Pokemon'][q]["Item"]
			trainerData[i]['Pokemon'][q]["Moves"] = trainerData[tmapdict[i]]['Pokemon'][q]["Moves"]
			trainerData[i]['Pokemon'][q]["NewCode"] = trainerData[tmapdict[i]]['Pokemon'][q]["NewCode"]
	return trainerData