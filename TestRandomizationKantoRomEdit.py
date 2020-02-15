import LoadLocationData
import Badge
import RandomizeItems
import RandomizerRom
import PokemonRandomizer
from collections import defaultdict

res = LoadLocationData.LoadDataFromFolder(".")
trashItems = res[1]
LocationList = res[0]
progressItems = ['Surf', 'Squirtbottle', 'Flash', 'Mystery Egg', 'Cut', 'Strength', 'Secret Potion','Red Scale', 'Whirlpool','Card Key', 'Basement Key', 'Waterfall', 'S S Ticket','Bicycle','Machine Part', 'Lost Item']
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
Thunder = Badge.Badge()
Thunder.isTrash = True
Thunder.Name = 'Thunder Badge'
Marsh = Badge.Badge()
Marsh.isTrash = True
Marsh.Name = 'Marsh Badge'
Rainbow = Badge.Badge()
Rainbow.isTrash = True
Rainbow.Name = 'Rainbow Badge'
Soul = Badge.Badge()
Soul.isTrash = True
Soul.Name = 'Soul Badge'
Cascade = Badge.Badge()
Cascade.isTrash = True
Cascade.Name = 'Cascade Badge'
Boulder = Badge.Badge()
Boulder.isTrash = True
Boulder.Name = 'Boulder Badge'
Volcano = Badge.Badge()
Volcano.isTrash = True
Volcano.Name = 'Volcano Badge'
Earth = Badge.Badge()
Earth.isTrash = True
Earth.Name = 'Earth Badge'
BadgeDict = {'Fog Badge':Fog, 'Zephyr Badge':Zephyr, 'Hive Badge':Hive, 'Plain Badge': Plain, 'Storm Badge': Storm, 'Mineral Badge': Mineral, 'Glacier Badge': Glacier, 'Rising Badge': Rising, 'Thunder Badge': Thunder, 'Marsh Badge' : Marsh, 'Rainbow Badge': Rainbow, 'Soul Badge': Soul, 'Cascade Badge': Cascade,'Boulder Badge': Boulder, 'Volcano Badge': Volcano, 'Earth Badge': Earth}
result = RandomizeItems.RandomizeItems('None',LocationList,progressItems,trashItems,BadgeDict,inputFlags = ['Kanto Mode'])
print('-------')
for j in result[0]:
	i = result[0][j]
	if(i.NormalItem is None and i.isItem()):
		print(i.Name)
print('-------')
for j in result[0]:
	i = result[0][j]
	if(i.NormalItem is not None and not i.isItem()):
		print(i.Name)
monFun = PokemonRandomizer.generateRandomMonFun(result[2],result[0])
banMap = defaultdict(lambda: [],{'FALKNER 1':['FISHER 11','CLAIR 1', 'BROCK 1'],'BUGSY 1':['CHAMPION 1']})
newTree = PokemonRandomizer.randomizeTrainers(result[0],85,lambda y: monFun(y,1001,85),True,banMap)
RandomizerRom.DirectWriteItemLocations(result[0].values())
RandomizerRom.WriteTrainerLevels(result[0], result[2],newTree)
RandomizerRom.WriteWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
RandomizerRom.WriteSpecialWildLevels(result[0], result[2],lambda x,y: monFun(x,y,85))
print(result[2])
print(result[1])
