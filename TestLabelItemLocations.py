import LoadLocationData
import Badge
import RandomizeItems
import RandomizerRom
import PokemonRandomizer
from collections import defaultdict

res = LoadLocationData.LoadDataFromFolder(".")
trashItems = res[1]
LocationList = LoadLocationData.FlattenLocationTree(res[0])

RandomizerRom.ResetRom()
RandomizerRom.LabelAllLocations(LocationList)