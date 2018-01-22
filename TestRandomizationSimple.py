import LoadLocationData as LocationData
import Badge
import RandomizeItems
import RandomizerRom

trashItems = LocationData.trashList;
progressItems = ['Surf', 'Squirtbottle', 'Flash', 'Mystery Egg', 'Cut']
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
print(result[1])
RandomizerRom.ResetRom()
RandomizerRom.WriteItemLocations(result[0].values())
RandomizerRom.WriteTrainerLevels(result[0], result[2])
