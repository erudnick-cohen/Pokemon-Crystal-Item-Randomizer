import csv
from collections import defaultdict
import random

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
def randomizeTrainers(range,monFun):
	#load in base stat information
	with open('pokedex.csv', newline='') as csvfile:
		reader = csv.reader(csvfile)
		for i in reader:
			bstMap[i[1].upper()] = int(i[2])
	#load up the trainer data
	yamlfile = open("TrainerData/Trainers.yaml")
	yamltext = yamlfile.read()
	trainerData = yaml.load(yamltext)
	
	#for trainers who don't have moves, randomizing the trainer file is just randomizing pokemon
	#for trainers who DO have moves, we SHUFFLE their pokemon with those of other trainers with moves
	mList = []
	for i in trainerData:
		trainerData[i]['NewCode'] = trainerData[i]['Code']
		if(trainerData[i]['Type'] == 'TRAINERTYPE_MOVES'):
			for j in range(0,len(trainerData[i]["Pokemon"])):
				mList.append(i,j,bstMap[trainerData[i]["Pokemon"][j]])