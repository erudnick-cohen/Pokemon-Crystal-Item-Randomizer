import os
import shutil

def UpdateLabels(wsl=False, delete_file=False):

    os.chdir('RandomizerRom')
    try:
        os.remove('pokecrystal-speedchoice.gbc')
    except OSError:
        pass

    make_command = 'make'
    ruby_commands = 'ruby ../generate-label-details.rb; ruby ../warp_data_labels.rb'

    if wsl:
        make_command = "wsl " + make_command
        ruby_commands = "wsl " + ruby_commands

    os.system(make_command)
    os.system(ruby_commands)
    # delete the compiled rom once we're done, we don't need that, we need the offsets
    try:
        if delete_file:
            os.remove('pokecrystal-speedchoice.gbc')
    except OSError:
        pass
    os.chdir('..')
    # remove old label details
    try:
        os.remove('Warp Data/crystal-speedchoice-warp-label-details.json')
        os.remove('crystal-speedchoice-label-details.json')
    except OSError:
        pass
    shutil.move(r'RandomizerRom/crystal-speedchoice-label-details.json', os.getcwd())
    shutil.move(r'RandomizerRom/crystal-speedchoice-warp-label-details.json', os.getcwd()+"/Warp Data")

    # DONT FORGET TO COMMIT THE CHANGED FILES THIS SCRIPT PRODUCES!!!!



if __name__ == '__main__':
    #import, and thus run TestLabelItemLocations

    UpdateLabels()




