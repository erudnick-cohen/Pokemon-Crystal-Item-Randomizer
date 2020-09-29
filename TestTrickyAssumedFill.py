import RunCustomRandomizationAssumedFill as RunCustomRandomization
import yaml
import json

romPath = 'testTrickyAgainBase - Copy.gbc'
yamlfile = open("Modes/Tricky.yml")
yamltext = yamlfile.read()
settings = yaml.load(yamltext)
yamlfile = open(settings['BasePatch'])
yamltext = yamlfile.read()
patches = json.loads(yamltext)
modFileList = settings['DefaultModifiers']
modList = []
plandoPlacements = {"Hidden Machine Part" : "Radio Card", "Route 29 Potion" : "Squirtbottle", "Route 30 Berry Man" : "Pokegear", "Violet City Gym Badge": "Fog Badge", "Falkner TM" : "Surf", "Route 31 Pokeball" : "Cut", 'Goldenrod City Gym' : "Hive Badge", "Route 30 Antidote" : "Pass"}
for i in modFileList:
	yamlfile = open(i)
	yamltext = yamlfile.read()
	modList.append(yaml.load(yamltext))
res = RunCustomRandomization.randomizeRom(romPath,settings['Goal'], settings['FlagsSet'],patches, banList = settings['BannedLocations'], allowList = settings['AllowedLocations'], modifiers = modList, plandoPlacements = plandoPlacements)
print(res[2])
print(res[1])