from LoadLocationData import purgeWarpBidirectional as purge
from RandomizeFunctions import RandomItemProcessor

warpLocationsTest1 = [
    {"Start Warp Group": "A",
     "End Warp Group": "B",
     },

{"Start Warp Group": "A",
     "End Warp Group": "C",
     },

{"Start Warp Group": "A",
     "End Warp Group": "D",
     },

{"Start Warp Group": "A",
     "End Warp Group": "E",
     },

{"Start Warp Group": "B",
     "End Warp Group": "C",
     },

{"Start Warp Group": "C",
     "End Warp Group": "D",
     },

{"Start Warp Group": "C",
     "End Warp Group": "B",
     },

{"Start Warp Group": "D",
     "End Warp Group": "A",
     },

{"Start Warp Group": "E",
     "End Warp Group": "A",
     },

]

warpLocationsTest2 = [
    {"Start Warp Group": "A",
     "End Warp Group": "B",
     },

{"Start Warp Group": "A",
     "End Warp Group": "C",
     },

{"Start Warp Group": "A",
     "End Warp Group": "D",
     },

{"Start Warp Group": "D",
     "End Warp Group": "A",
     },

{"Start Warp Group": "D",
     "End Warp Group": "E",
     },

{"Start Warp Group": "E",
     "End Warp Group": "D",
     },


]



warpLocationsTest3 = [
    {"Start Warp Group": "A",
     "End Warp Group": "B",
     },

{"Start Warp Group": "B",
     "End Warp Group": "C",
     },

{"Start Warp Group": "B",
     "End Warp Group": "E",
     },


{"Start Warp Group": "C",
     "End Warp Group": "D",
     },


{"Start Warp Group": "B",
     "End Warp Group": "A",
     },

{"Start Warp Group": "C",
     "End Warp Group": "B",
     },

{"Start Warp Group": "E",
     "End Warp Group": "B",
     },

{"Start Warp Group": "D",
     "End Warp Group": "C",
     },

{"Start Warp Group": "A",
     "End Warp Group": "F",
     },

{"Start Warp Group": "F",
     "End Warp Group": "G",
     },

{"Start Warp Group": "G",
     "End Warp Group": "A",
     },


]



warpLocationsTest4 = [
    {"Start Warp Group": "A",
     "End Warp Group": "B",
     },

{"Start Warp Group": "B",
     "End Warp Group": "A",
     }

]

items = RandomItemProcessor()

removalsTest1 = purge(warpLocationsTest1)
assert len(removalsTest1) == 3
assert warpLocationsTest1[4] in removalsTest1
assert warpLocationsTest1[7] in removalsTest1
assert warpLocationsTest1[8] in removalsTest1

removalsTest2 = purge(warpLocationsTest2)
assert len(removalsTest2) == 2
assert warpLocationsTest2[5] in removalsTest2
assert warpLocationsTest2[3] in removalsTest2

removalsTest3 = purge(warpLocationsTest3)
assert len(removalsTest3) == 4
assert warpLocationsTest3[4] in removalsTest3
assert warpLocationsTest3[5] in removalsTest3
assert warpLocationsTest3[6] in removalsTest3
assert warpLocationsTest3[7] in removalsTest3

removalsTest4 = purge(warpLocationsTest4)
assert len(removalsTest4) == 0