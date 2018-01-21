import LoadLocationData as LocationData
import Badge
import RandomizeItems

trashItems = LocationData.trashList;
trashItems.append('Pokedex')
progressItems = ['Surf', 'Squirtbottle', 'Flash', 'Mystery Egg', 'Rock Smash', 'Cut']
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
BadgeDict = {'Fog Badge':Fog, 'Zephyr Badge':Zephyr, 'Hive Badge':Hive, 'Plain Badge': Plain}
result = RandomizeItems.RandomizeItems('Route 32',LocationData.LocationList,progressItems,trashItems,BadgeDict)
print(result)