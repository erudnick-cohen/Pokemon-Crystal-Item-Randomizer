import sys

import GenerateHintData
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

    RandomizerRom.ResetRomForLabelling(wsl=has_wsl)

    sign_entries = GenerateHintData.GenerateHintLabels()
    TestLabels()
    GenerateWarpData.GenerateWarpLabels()
    GenerateMapLabels.GenerateWarpMapDataLabels()
    GenerateMapLabels.LabelAllBlocks()
    GenerateMapLabels.GenerateNPCLabels()

    UpdateLabelsScript.UpdateLabels(has_wsl, delete_file=False)

    GenerateMapLabels.CreateMapPatches()
    GenerateMapLabels.GenerateNPCSwitchPatch()

    GeneratePatches.makePatches()
    GenerateWarpData.interpretDataForMapIDs()

    GenerateHintData.createSignJson(sign_entries)