import re
import yaml
#open and parse the file
trainerfile = open("../RandomizerRom/data/trainers/parties.asm")
trainerstext = trainerfile.read()

#define the regex for parsing trainers (fix below the word fix to inlcude ampersands)
restring = '(; (\S+) \((\d+)\)\s+db \"([A-Z_& ?]+)@\"\s+db (\S+)\s+; party\s+(?:db \d+, [A-Z_]+(?:, [A-Z]+)?\s+(?:db (?:[A-Z_]|0)+\s+){0,4}\s+)+\s+db [$]ff ; end)'
regex = re.compile(restring)
results = regex.findall(trainerstext)

trainerDict = {};

#loop through each trainers entry and build dict of them, also pull out pokemon data
for i in results:
	dataDict = {};
	dataDict['Code'] = i[0]
	dataDict['Class'] = i[1]
	dataDict['Number'] = i[2]
	dataDict['Type'] = i[4]
	dataDict['Name'] = i[3]
	#parse out the pokemon
	pokere = '(db \d+, [A-Z_]+(?:, [A-Z_]+)?\s+(?:db [A-Z_]+\s+){0,4}\s+)'
	pokemon = []
	pokeregex = re.compile(pokere)
	pokeresults = pokeregex.findall(i[0])
	for j in pokeresults:
		pokedict = {}
		#grab the level, item and name of the pokemon via yet another regex
		pokedataregex = re.compile('db (\d+), ([A-Z_]+)(?:, ([A-Z_]+))?')
		m = pokedataregex.search(j)
		pokedict['Level'] = int(m.groups()[0])
		pokedict['Pokemon'] = m.groups()[1]
		pokedict['Item'] = m.groups()[2]
		moveregex = re.compile('db ([A-Z_]+)')
		moves = moveregex.findall(j)
		moveList = []
		for k in moves:
			moveList.append(k)
		pokedict['Moves'] = moveList
		pokemon.append(pokedict)
	dataDict['Pokemon'] = pokemon
	trainerDict[i[1]+" "+i[2]] = dataDict
stream = open('Trainers.yaml', 'w')
yaml.dump(trainerDict, stream,default_flow_style=False)    # Write a YAML representation of data to 'document.yaml'.
print(yaml.dump(trainerDict,default_flow_style=False))      # Output the document to the screen.