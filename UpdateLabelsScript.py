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
os.chdir('..')
shutil.copyfile(r'RandomizerRom/crystal-speedchoice-label-details.json', '.')
GeneratePatches.makePatches()

#DONT FORGET TO COMMIT THE CHANGED FILES THIS SCRIPT PRODUCES!!!!