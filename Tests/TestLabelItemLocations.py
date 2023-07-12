import LoadLocationData
import Badge
import RandomizeItems
import RandomizerRom
import PokemonRandomizer
import yaml
from collections import defaultdict

def TestLabels():
    res = LoadLocationData.LoadDataFromFolder(".", labelling=True, flags=["No Ban"])
    trashItems = res[1]
    LocationList = LoadLocationData.FlattenLocationTree(res[0])
    yamlfile = open("./TrainerData/Trainers.yaml")
    yamltext = yamlfile.read()
    trainerData = yaml.load(yamltext, Loader=yaml.FullLoader)

    RandomizerRom.LabelAllLocations(LocationList)
    # RandomizerRom.LabelTrainerData(trainerData) #disabled because new speedchoice has different format for these
    # RandomizerRom.LabelWild() # See above
    # RandomizerRom.LabelSpecialWild(LocationList) # See above


if __name__ == '__main__':
    TestLabels()
