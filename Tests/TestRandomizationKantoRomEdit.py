import LoadLocationData
import Badge
import RandomizeItems
import RandomizerRom
import PokemonRandomizer
import yaml
import json
import mmap
from collections import defaultdict

import Static

res = LoadLocationData.LoadDataFromFolder("..")
trashItems = res[1]
LocationList = res[0]
progressItems = ['Surf', 'Squirtbottle', 'Flash', 'Mystery Egg', 'Cut', 'Strength', 'Secret Potion','Red Scale', 'Whirlpool','Card Key', 'Basement Key', 'Waterfall', 'S S Ticket','Bicycle','Machine Part', 'Lost Item','Pass']
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
Storm.isTrash = True
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
result = RandomizeItems.RandomizeItems('None',LocationList,progressItems,trashItems,BadgeDict,inputFlags = ['Kanto Mode'])
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

yamlfile = open("../"+Static.default_labels_file)
yamltext = yamlfile.read()
addressLists = json.loads(yamltext)
addressData = {}
for i in addressLists:
	addressData[i['label'].split(".")[-1]] = i
print(addressData)

#newTree = PokemonRandomizer.randomizeTrainers(result[0],85,lambda y: monFun(y,1001,85),True,banMap)

f = open('crystal-speedchoice-v6.0.gbc','r+b')
romMap = mmap.mmap(f.fileno(),0)
RandomizerRom.DirectWriteItemLocations(result[0].values(), addressData,romMap)
RandomizerRom.WriteWildLevelsToMemory(result[0], result[2],addressData,romMap)
RandomizerRom.WriteSpecialWildToMemory(result[0], result[2],addressData,romMap)
RandomizerRom.WriteTrainerDataToMemory(result[0],result[2],addressData,romMap)
yamlfile = open("../item-randomizer-patches-diff-speedchoice.json")
yamltext = yamlfile.read()
patches = json.loads(yamltext)
RandomizerRom.ApplyGamePatches(romMap,patches)
#RandomizerRom.WriteTrainerLevels(result[0], result[2],newTree)
#RandomizerRom.WriteWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
#RandomizerRom.WriteSpecialWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
print(result[2])
print(result[1])
