import RunCustomRandomizationAssumedFill as RunCustomRandomization
import yaml
import json
from shutil import copyfile

romPath = 'testTrickyAgainBase - Copy.gbc'
copyfile(romPath, 'Hmmm'+romPath)

yamlfile = open("Modes/Tricky.yml")
yamltext = yamlfile.read()
settings = yaml.load(yamltext, Loader=yaml.FullLoader)
yamlfile = open(settings['BasePatch'])
yamltext = yamlfile.read()
patches = json.loads(yamltext)
modFileList = settings['DefaultModifiers']
modList = []
#plandoPlacements = {"Hidden Machine Part" : "Radio Card", "Route 29 Potion" : "Squirtbottle", "Route 30 Berry Man" : "OLD_ROD", "Violet City Gym Badge": "Storm Badge", "Falkner TM" : "Fly", "Route 31 Pokeball" : "Cut", 'Goldenrod City Gym' : "Hive Badge", "Route 30 Antidote" : "Pass", 'Azalea Town Gym Badge': 'Fog Badge', 'Buena Item': "GOOD_ROD"}
#plandoPlacements = {'Celadon City Gym Badge':'Fog Badge' }
plandoPlacements = {}
CoreProgress = ['Surf','Fog Badge', 'Pass', 'S S Ticket', 'Squirtbottle']
for i in modFileList:
	yamlfile = open(i)
	yamltext = yamlfile.read()
	modList.append(yaml.load(yamltext, Loader=yaml.FullLoader))
res = RunCustomRandomization.randomizeRom('Hmmm'+romPath,settings['Goal'], settings['FlagsSet'],patches, banList = settings['BannedLocations'], allowList = settings['AllowedLocations'], modifiers = modList, plandoPlacements = plandoPlacements, coreProgress = CoreProgress)
print(res[2])
print(res[1])