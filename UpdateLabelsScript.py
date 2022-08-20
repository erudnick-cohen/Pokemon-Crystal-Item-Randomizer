import os
import shutil
import GeneratePatches

#import, and thus run TestLabelItemLocations
import GenerateWarpData
import GenerateMapLabels
from Tests.TestLabelItemLocations import *
#import sys
#sys.exit(0)

GenerateWarpData.GenerateWarpLabels()
GenerateMapLabels.GenerateWarpMapDataLabels()
GenerateMapLabels.LabelAllBlocks()

os.chdir('RandomizerRom')
try:
    os.remove('pokecrystal-speedchoice.gbc')
except OSError:
    pass
os.system('make')
os.system(r'ruby ../generate-label-details.rb')
#delete the compiled rom once we're done, we don't need that, we need the offsets
try:
    os.remove('pokecrystal-speedchoice.gbc')
except OSError:
    pass
os.chdir('..')
#remove old label details
try:
    os.remove('crystal-speedchoice-label-details.json')
except OSError:
    pass
shutil.move(r'RandomizerRom/crystal-speedchoice-label-details.json', os.getcwd())
GenerateMapLabels.CreateMapPatches()
GeneratePatches.makePatches()

#DONT FORGET TO COMMIT THE CHANGED FILES THIS SCRIPT PRODUCES!!!!


