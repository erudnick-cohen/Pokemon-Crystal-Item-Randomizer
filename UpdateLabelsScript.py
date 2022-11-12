import os
import shutil
import subprocess
import sys
import threading

import Static


class ProcessPrint(threading.Thread):
    stream=None
    output=None
    allOutput=None

    def __init__(self, dataStream, output):
        threading.Thread.__init__(self)
        self.stream = dataStream
        self.output = output
        self.allOutput = []

    def run(self):
        for item in self.stream:
            item = item.strip()
            print(item, file=self.output)
            self.output.flush()
            self.allOutput.append(item)

def BuildRom(out_file, delete_file=False, wsl=False, change_dir=True):
    if change_dir:
        os.chdir("RandomizerRom")
    make_command = 'make'

    if wsl:
        make_command = "wsl " + make_command

    process = subprocess.Popen(make_command, universal_newlines=True, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = ProcessPrint(process.stdout, sys.stdout)
    error = ProcessPrint(process.stderr, sys.stderr)

    output.start()
    error.start()
    output.join()
    error.join()

    error_result = error.allOutput
    if len(error_result) > 0:
        print("Errors occured building rom")
        return False


    # delete the compiled rom once we're done, we don't need that, we need the offsets
    try:
        if delete_file:
            os.remove(out_file)
    except OSError:
        print("Unable to delete file")
        return False

    if change_dir:
        os.chdir("..")

    return True


def LoadSym(sym_file):
    sym_file_obj = open(sym_file)
    lines = sym_file_obj.readlines()
    sym_file_obj.close()

    return [ x.strip() for x in lines]


def CompareSyms(pre_sym, post_sym, definedLabels):
    # Post sym will contain many more labels
    # But  all lines in pre_sym should also be in post_sym
    # If a label is in a different location, this will cause a failure

    # Cannot just check all lines though
    # Some patch generation can:
    # Move a label around within its block (eg Togepi egg hatch)
    # Render a label obsolete (eg Sailor Huey)

    # This requires adding some redundant labels for labels which are not part of the compilation
    # Such as Huey Fight 0, which is not normally used in the patch data

    result = True

    for line in pre_sym:
        if line not in post_sym:

            sym_split = line.split(" ")
            labelName = sym_split[1]
            # No issue if reference is not found due to change in defined label within a patch section
            matches = [ x for x in definedLabels if x in labelName ]
            if len(matches) == 0:
                print("Sym line not found::", line)
                result = False

    return result

def BuildScriptFromSym(wsl=False, change_dir=True):
    if change_dir:
        os.chdir("RandomizerRom")
    ruby_commands = 'ruby ../generate-label-details.rb; ruby ../warp_data_labels.rb ;' \
                    'ruby ../generate-hint-details.rb; ruby ../block-labels.rb'

    if wsl:
        ruby_commands = "wsl " + ruby_commands

    process = subprocess.Popen(ruby_commands, universal_newlines=True, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = ProcessPrint(process.stdout, sys.stdout)
    error = ProcessPrint(process.stderr, sys.stderr)

    output.start()
    error.start()
    output.join()
    error.join()

    error_result = error.allOutput
    if len(error_result) > 0:
        # allow some types of errors
        cut_errors = [ error for error in error_result if "Insecure world writable dir" not in error and
                       "generated crystal-speedchoice" not in error and
                       "warning:" not in error
                       ]
        if len(cut_errors) > 0:
            print("Errors occured with ruby scripts")
            print(error_result)
            return False

    if change_dir:
        os.chdir("..")

    return True

def UpdateLabels(wsl=False, delete_file=False):



    try:
        if os.path.isfile(Static.warp_labels_file):
            os.remove(Static.warp_labels_file)
        if os.path.isfile(Static.hint_labels_file):
            os.remove(Static.hint_labels_file)
        if os.path.isfile(Static.blocks_labels_file):
            os.remove(Static.blocks_labels_file)
        if os.path.isfile(Static.default_labels_file):
            os.remove(Static.default_labels_file)

        os.chdir('RandomizerRom')

        if os.path.isfile(Static.speedchoice_build_out_file):
            os.remove(Static.speedchoice_build_out_file)


    except OSError as ose:
        print("OS Error occurred")
        raise ose

    build_success = BuildRom(Static.speedchoice_build_out_file, delete_file, wsl, change_dir=False)
    if not build_success:
        return False

    ruby_success = BuildScriptFromSym(wsl, change_dir=False)
    if not ruby_success:
        return False


    os.chdir('..')
    # remove old label details
    try:
        os.remove(Static.warp_labels_file)
        os.remove(Static.default_labels_file)
        os.remove(Static.hint_labels_file)
        os.remove(Static.blocks_labels_file)
    except OSError:
        pass

    shutil.move("RandomizerRom/"+Static.default_labels_file, os.getcwd())
    shutil.move('RandomizerRom/'+"crystal-speedchoice-warp-label-details.json", os.getcwd()+"/Warp Data")
    shutil.move('RandomizerRom/'+"crystal-speedchoice-hint-details.json", os.getcwd()+"/Config")
    shutil.move('RandomizerRom/'+"crystal-speedchoice-block-details.json", os.getcwd()+"/Config")

    # DONT FORGET TO COMMIT THE CHANGED FILES THIS SCRIPT PRODUCES!!!!

    return True



if __name__ == '__main__':
    #import, and thus run TestLabelItemLocations

    UpdateLabels()




