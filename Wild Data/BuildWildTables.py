import re
import yaml
from collections import defaultdict

grassDict = {}
swarmDict = {}
surfDict = {}
#define the regex for parsing grass
#groups, 1 mapname, 2 not things that matter, 3 morning, 4 day, 5 night
restringgrass = '(map (\S+)\s+([ a-zA-Z0-9;:,/]*)\s+; morn\s+((?:db \d+, \S+\s+)+)\s*; day\s+((?:db \d+, \S+\s+)+)\s*; nite\s+((?:db \d+, \S+\s+)+))'
restringwater = '(map (\S+)\s+([ a-zA-Z0-9;:,/]*)\s+((?:db \d+, \S+\s+)+)\s*)'

#open and parse the file for johto grass
grassfile = open("../RandomizerRom/data/wild/johto_grass.asm")
grasstext = grassfile.read()
regex = re.compile(restringgrass)
results = regex.findall(grasstext)

for i in results:
	dataDict = {}
	print(i[1])
	dataDict["Name"] = i[1]
	dataDict["Code"] = i[0]
	dataDict["File"] = 'johto_grass.asm'
	monDict = defaultdict(list);
	monstring = '(db (\d+), (\S+)\s+)'
	monre = re.compile(monstring)
	monres = []
	minLV = 1000
	for j in range(3,5):
		monres.extend(monre.findall(i[j]))
	for j in monres:
		if(int(j[1]) not in monDict[j[2]]):
			monDict[j[2]].append(int(j[1]))
		minLV = min(minLV,int(j[1]))
	dataDict["Pokemon"] = dict(monDict);
	dataDict["Level"] = minLV
	grassDict[i[1]] = dataDict

	#open and parse the file for kanto grass
grassfile = open("../RandomizerRom/data/wild/kanto_grass.asm")
grasstext = grassfile.read()
regex = re.compile(restringgrass)
results = regex.findall(grasstext)

for i in results:
	dataDict = {}
	print(i[1])
	dataDict["Name"] = i[1]
	dataDict["Code"] = i[0]
	dataDict["File"] = 'kanto_grass.asm'
	monDict = defaultdict(list)
	monstring = '(db (\d+), (\S+)\s+)'
	monre = re.compile(monstring)
	monres = []
	minLV = 1000
	for j in range(3,5):
		monres.extend(monre.findall(i[j]))
	for j in monres:
		if(int(j[1]) not in monDict[j[2]]):
			monDict[j[2]].append(int(j[1]))
		minLV = min(minLV,int(j[1]))
	dataDict["Pokemon"] = dict(monDict)
	dataDict["Level"] = minLV
	grassDict[i[1]] = dataDict
	
#open and parse the file for swar,s
grassfile = open("../RandomizerRom/data/wild/swarm_grass.asm")
grasstext = grassfile.read()
regex = re.compile(restringgrass)
results = regex.findall(grasstext)

for i in results:
	dataDict = {}
	print(i[1])
	dataDict["Name"] = i[1]
	dataDict["Code"] = i[0]
	dataDict["File"] = 'swarm_grass.asm'
	monDict = defaultdict(list)
	monstring = '(db (\d+), (\S+)\s+)'
	monre = re.compile(monstring)
	monres = []
	minLV = 1000
	for j in range(3,5):
		monres.extend(monre.findall(i[j]))
	for j in monres:
		if(int(j[1]) not in monDict[j[2]]):
			monDict[j[2]].append(int(j[1]))
		minLV = min(minLV,int(j[1]))
	dataDict["Pokemon"] = dict(monDict)
	dataDict["Level"] = minLV
	swarmDict[i[1]] = dataDict
	
waterfile = open("../RandomizerRom/data/wild/kanto_water.asm")
watertext = waterfile.read()
regex = re.compile(restringwater)
results = regex.findall(watertext)
for i in results:
	dataDict = {}
	print(i[1])
	dataDict["Name"] = i[1]
	dataDict["Code"] = i[0]
	dataDict["File"] = 'kanto_water.asm'
	monDict = defaultdict(list)
	monstring = '(db (\d+), (\S+)\s+)'
	monre = re.compile(monstring)
	monres = []
	minLV = 1000
	monres.extend(monre.findall(i[3]))
	for j in monres:
		if(int(j[1]) not in monDict[j[2]]):
			monDict[j[2]].append(int(j[1]))
		minLV = min(minLV,int(j[1]))
	dataDict["Pokemon"] = dict(monDict);
	dataDict["Level"] = minLV
	surfDict[i[1]] = dataDict

waterfile = open("../RandomizerRom/data/wild/johto_water.asm")
watertext = waterfile.read()
regex = re.compile(restringwater)
results = regex.findall(watertext)
for i in results:
	dataDict = {}
	print(i[1])
	dataDict["Name"] = i[1]
	dataDict["Code"] = i[0]
	dataDict["File"] = 'johto_water.asm'
	monDict = defaultdict(list)
	monstring = '(db (\d+), (\S+)\s+)'
	monre = re.compile(monstring)
	monres = []
	minLV = 1000
	monres.extend(monre.findall(i[3]))
	for j in monres:
		if(int(j[1]) not in monDict[j[2]]):
			monDict[j[2]].append(int(j[1]))
		minLV = min(minLV,int(j[1]))
	dataDict["Pokemon"] = dict(monDict)
	dataDict["Level"] = minLV
	surfDict[i[1]] = dataDict

stream = open('surfGrass.yaml', 'w')
yaml.dump(surfDict, stream,default_flow_style=False)    # Write a YAML representation of data to 'document.yaml'.
print(yaml.dump(surfDict,default_flow_style=False))      # Output the document to the screen.
stream = open('wildGrass.yaml', 'w')
yaml.dump(grassDict, stream,default_flow_style=False)    # Write a YAML representation of data to 'document.yaml'.
print(yaml.dump(grassDict,default_flow_style=False))      # Output the document to the screen.