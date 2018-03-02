import LoadLocationData as LocationData
import Badge
import RandomizeItems
import RandomizerRom
import PokemonRandomizer
from collections import defaultdict

trashItems = LocationData.trashList;
progressItems = ['Surf', 'Squirtbottle', 'Flash', 'Mystery Egg', 'Cut', 'Strength', 'Secret Potion','Red Scale', 'Whirlpool','Card Key', 'Basement Key', 'Waterfall']
Zephyr = Badge.Badge()
Zephyr.isTrash = False
Zephyr.Name = 'Zephyr Badge'
Fog = Badge.Badge()
Fog.isTrash = False
Fog.Name = 'Fog Badge'
Hive = Badge.Badge()
Hive.isTrash = False
Hive.Name = 'Hive Badge'
Plain = Badge.Badge()
Plain.isTrash = False
Plain.Name = 'Plain Badge'
Storm = Badge.Badge()
Storm.isTrash = True
Storm.Name = 'Storm Badge'
Mineral = Badge.Badge()
Mineral.isTrash = True
Mineral.Name = 'Mineral Badge'
Glacier = Badge.Badge()
Glacier.isTrash = False
Glacier.Name = 'Glacier Badge'
Rising = Badge.Badge()
Rising.isTrash = False
Rising.Name = 'Rising Badge'
BadgeDict = {'Fog Badge':Fog, 'Zephyr Badge':Zephyr, 'Hive Badge':Hive, 'Plain Badge': Plain, 'Storm Badge': Storm, 'Mineral Badge': Mineral, 'Glacier Badge': Glacier, 'Rising Badge': Rising}
result = RandomizeItems.RandomizeItems('None',LocationData.LocationList,progressItems,trashItems,BadgeDict)
monFun = PokemonRandomizer.generateRandomMonFun(result[2],result[0])
banMap = defaultdict(lambda: [],{'FALKNER 1':['FISHER 11','CLAIR 1'],'BUGSY 1':['CHAMPION 1']})
newTree = PokemonRandomizer.randomizeTrainers(result[0],85,lambda y: monFun(y,1001,85),True,banMap)
RandomizerRom.ResetRom()
RandomizerRom.WriteItemLocations(result[0].values())
RandomizerRom.WriteTrainerLevels(result[0], result[2],newTree)
RandomizerRom.WriteWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
RandomizerRom.WriteSpecialWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
print(result[2])
print(result[1])