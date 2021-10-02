import RunCustomRandomizationAssumedFill as RunCustomRandomization
import yaml
import json
import random

romPath = 'crystal-speedchoice-v6.0.gbc'
yamlfile = open("Modes/JohtoMode.yml")
yamltext = yamlfile.read()
settings = yaml.load(yamltext, Loader=yaml.FullLoader)
yamlfile = open(settings['BasePatch'])
yamltext = yamlfile.read()
patches = json.loads(yamltext)
modFileList = settings['DefaultModifiers']
modList = []
plandoPlacements = {}
progressItems = settings['ProgressItems']
for i in modFileList:
	yamlfile = open(i)
	yamltext = yamlfile.read()
	modList.append(yaml.load(yamltext, Loader=yaml.FullLoader))
res = RunCustomRandomization.randomizeRom('Hmmm'+romPath,settings['Goal'], random.random()*1000, settings['FlagsSet'],patches, banList = settings['BannedLocations'], allowList = settings['AllowedLocations'], modifiers = modList, plandoPlacements = plandoPlacements, otherSettings = settings, requiredItems = progressItems)
print(res[2])
print(res[1])