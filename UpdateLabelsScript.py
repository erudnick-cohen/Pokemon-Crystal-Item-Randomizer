import os
import shutil

#import, and thus run TestLabelItemLocations
import TestLabelItemLocations
os.chdir('RandomizerRom')
os.remove('pokecrystal-speedchoice.gbc')
os.system('ruby generate-label-details.rb')
os.chdir('..')
shutil.copyfile(r'RandomizerRom\crystal-speedchoice-label-details.json', '.')

#DONT FORGET TO COMMIT THE CHANGED FILES THIS SCRIPT PRODUCES!!!!