import sys

import GenerateHintData
import UpdateLabelsScript
import GenerateWarpData
import GenerateMapLabels
from Tests.TestLabelItemLocations import *
import RandomizerRom
import GeneratePatches

if __name__ == '__main__':
    RandomizerRom.ResetRomForLabelling()

    sign_entries = GenerateHintData.GenerateHintLabels()
    TestLabels()
    GenerateWarpData.GenerateWarpLabels()
    GenerateMapLabels.GenerateWarpMapDataLabels()
    GenerateMapLabels.LabelAllBlocks()
    GenerateMapLabels.GenerateNPCLabels()

    UpdateLabelsScript.UpdateLabels(wsl=True, delete_file=False)

    GenerateMapLabels.CreateMapPatches()
    GenerateMapLabels.GenerateNPCSwitchPatch()

    GeneratePatches.makePatches()
    GenerateWarpData.interpretDataForMapIDs()

    GenerateHintData.createSignJson(sign_entries)