import sys

import GenerateHintData
import UpdateLabelsScript
import GenerateWarpData
from Tests.TestLabelItemLocations import *
import RandomizerRom
import GeneratePatches

if __name__ == '__main__':
    RandomizerRom.ResetRomForLabelling()
    #sys.exit(1)
    sign_entries = GenerateHintData.GenerateHintLabels()
    TestLabels()
    GenerateWarpData.GenerateWarpLabels()

    UpdateLabelsScript.UpdateLabels(wsl=True, delete_file=False)

    GeneratePatches.makePatches()
    GenerateWarpData.interpretDataForMapIDs()
    GenerateHintData.createSignJson(sign_entries)