from contextlib import contextmanager
import sys, os, time
import RunCustomRandomizationAssumedFill as RunCustomRandomization
import yaml
import json
from shutil import copyfile
import locations_dict

@contextmanager
def suppress_stdout_stderr():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull

        old_stderr = sys.stderr
        sys.stderr = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def print_dict(mydict):
        for key in mydict.keys():
                value = mydict[key]
                print(str(key) + ":" + str(value))

with suppress_stdout_stderr():
        romPath = 'testTrickyAgainBase - Copy.gbc'
        copyfile(romPath, 'Hmmm'+romPath)

        yamlfile = open("Modes/Extreme.yml")
        yamltext = yamlfile.read()
        settings = yaml.load(yamltext, Loader=yaml.FullLoader)
        yamlfile = open(settings['BasePatch'])
        yamltext = yamlfile.read()
        patches = json.loads(yamltext)
        modFileList = settings['DefaultModifiers']
        modFileList.append('Modifiers/HiddenItems.yml')
        modList = []
        plandoPlacements = {}
        CoreProgress = ['Surf','Fog Badge', 'Pass', 'S S Ticket', 'Squirtbottle']
        for i in modFileList:
                yamlfile = open(i)
                yamltext = yamlfile.read()
                modList.append(yaml.load(yamltext, Loader=yaml.FullLoader))

locs = locations_dict.locs
print('Finished initialization')
starttime = time.time()
for run in range(3000):
        currstarttime = time.time()

        with suppress_stdout_stderr():
                res = RunCustomRandomization.randomizeRom('Hmmm'+romPath,settings['Goal'], settings['FlagsSet'],patches, banList = settings['BannedLocations'], allowList = settings['AllowedLocations'], modifiers = modList, plandoPlacements = plandoPlacements, coreProgress = CoreProgress, otherSettings = {'BadgeItemShuffle':None})

        itemsToFind = ['Surf', 'Fog Badge']
        for x in range(len(itemsToFind)):
                curr_item = itemsToFind[x]
                curr_location = res[1][curr_item]
                if curr_location in locs.keys():
                        locs[curr_location] += 1
                else:
                        print('Error: Missing ' + curr_location)
        currendtime = time.time()
        currdiff = currendtime - currstarttime
        currtotaldiff = currendtime - starttime
        curravg = currtotaldiff / (run + 1)
        print("Run: " + str(run) + ", " + f'{currdiff:.2f}' + " sec" + ", " + f'{curravg:.2f}' + " sec avg")
        
print_dict(locs)
endtime = time.time()
timediff = endtime - starttime
print(f'{timediff:.2f}' + ' sec')
