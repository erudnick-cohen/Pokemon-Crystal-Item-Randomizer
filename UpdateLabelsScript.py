import os
import shutil
import GeneratePatches

#import, and thus run TestLabelItemLocations
import TestLabelItemLocations
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
shutil.copyfile(r'RandomizerRom/crystal-speedchoice-label-details.json', '.')
GeneratePatches.makePatches()

#DONT FORGET TO COMMIT THE CHANGED FILES THIS SCRIPT PRODUCES!!!!