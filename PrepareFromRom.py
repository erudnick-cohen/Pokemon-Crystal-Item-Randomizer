import json
import os
import sys

import GenerateHintData
import GenerateItemLabels
import RandomizeFunctions
import Static
import UpdateLabelsScript
import GenerateWarpData
import GenerateMapLabels
from Tests.TestLabelItemLocations import *
import RandomizerRom
import GeneratePatches

import shutil
import sys

if __name__ == '__main__':
    has_wsl = False

    result = shutil.which("wsl")
    if result is not None:
        has_wsl = True

    out_file = "crystal-speedchoice.gbc"
    sym_file = "RandomizerRom/crystal-speedchoice.sym"

    RandomizerRom.ResetRomForLabelling(wsl=has_wsl)
    print("DIR1",os.getcwd())
    build_success = UpdateLabelsScript.BuildRom(out_file, delete_file=True, wsl=has_wsl)
    print("DIR2", os.getcwd())
    if not build_success:
        print("Unable to build from base")
        raise Exception("Unable to build from base")

    pre_sym = UpdateLabelsScript.LoadSym(sym_file)
    definedLabels = []

    RandomizerRom.UpdateDataDirectory()

    RandomizerRom.InsertManualFiles(definedLabels)
    sign_entries = GenerateHintData.GenerateHintLabels()
    TestLabels()
    GenerateWarpData.GenerateWarpLabels()
    GenerateMapLabels.GenerateWarpMapDataLabels()
    GenerateMapLabels.LabelAllBlocks()
    GenerateMapLabels.GenerateNPCLabels()

    GenerateItemLabels.GenerateAttributeLabels()

    labelsSuccess = UpdateLabelsScript.UpdateLabels(has_wsl, delete_file=False)
    if not labelsSuccess:
        raise Exception("Failure to generate labels")

    post_sym = UpdateLabelsScript.LoadSym(sym_file)
    sym_match_up = UpdateLabelsScript.CompareSyms(pre_sym, post_sym, definedLabels)
    if not sym_match_up:
        raise Exception("Syms do not match")

    GenerateMapLabels.CreateMapPatches()
    GenerateMapLabels.GenerateNPCSwitchPatch()

    GeneratePatches.makePatches()
    GenerateWarpData.interpretDataForMapIDs()

    GenerateHintData.createSignJson(sign_entries)

    yamlfile = open(Static.default_labels_file, encoding='utf-8')
    yamltext = yamlfile.read()
    addressLists = json.loads(yamltext)
    addressData = {}
    for i in addressLists:
        addressData[i['label'].split(".")[-1]] = i

    majorVersion = addressData["ckir_BEFORE_MajorVersionNumber"]
    minorVersion = addressData["ckir_BEFORE_MinorVersionNumber"]
    revisionVersion = addressData["ckir_BEFORE_RevisionVersionNumber"]

    majorRequired = int(majorVersion["integer_values"][0])
    minorRequired = int(minorVersion["integer_values"][0])
    revisionRequired = int(revisionVersion["integer_values"][0])

    version_check = RandomizeFunctions.IsVersionSupported(majorRequired, minorRequired, revisionRequired)
    if not version_check:
        raise Exception("Version is invalid")
