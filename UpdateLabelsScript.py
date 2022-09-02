import os
import shutil

def UpdateLabels(wsl=False, delete_file=False):

    warp_labels_file = "Warp Data/crystal-speedchoice-warp-label-details.json"
    hint_labels_file = "Config/crystal-speedchoice-hint-details.json"
    blocks_labels_file = "Config/crystal-speedchoice-block-details.json"
    default_labels_file = "crystal-speedchoice-label-details.json"
    out_file = "pokecrystal-speedchoice.gbc"

    try:
        if os.path.isfile(warp_labels_file):
            os.remove(warp_labels_file)
        if os.path.isfile(hint_labels_file):
            os.remove(hint_labels_file)
        if os.path.isfile(blocks_labels_file):
            os.remove(blocks_labels_file)
        if os.path.isfile(default_labels_file):
            os.remove(default_labels_file)

        os.chdir('RandomizerRom')

        if os.path.isfile(out_file):
            os.remove(out_file)


    except OSError as ose:
        print("OS Error occurred")
        raise ose

    make_command = 'make'
    ruby_commands = 'ruby ../generate-label-details.rb; ruby ../warp_data_labels.rb ;' \
                    'ruby ../generate-hint-details.rb; ruby ../block-labels.rb'

    if wsl:
        make_command = "wsl " + make_command
        ruby_commands = "wsl " + ruby_commands

    os.system(make_command)
    os.system(ruby_commands)
    # delete the compiled rom once we're done, we don't need that, we need the offsets
    try:
        if delete_file:
            os.remove(out_file)
    except OSError:
        pass
    os.chdir('..')
    # remove old label details
    try:
        os.remove('Warp Data/crystal-speedchoice-warp-label-details.json')
        os.remove('crystal-speedchoice-label-details.json')
        os.remove('Config/crystal-speedchoice-hint-details.json')
        os.remove('Config/crystal-speedchoice-block-details.json')
    except OSError:
        pass
    shutil.move(r'RandomizerRom/crystal-speedchoice-label-details.json', os.getcwd())
    shutil.move(r'RandomizerRom/crystal-speedchoice-warp-label-details.json', os.getcwd()+"/Warp Data")
    shutil.move(r'RandomizerRom/crystal-speedchoice-hint-details.json', os.getcwd()+"/Config")
    shutil.move(r'RandomizerRom/crystal-speedchoice-block-details.json', os.getcwd()+"/Config")

    # DONT FORGET TO COMMIT THE CHANGED FILES THIS SCRIPT PRODUCES!!!!



if __name__ == '__main__':
    #import, and thus run TestLabelItemLocations

    UpdateLabels()




