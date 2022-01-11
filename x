diff --git a/Map Data/BlackthornGym.yml b/Map Data/BlackthornGym.yml
index 7356b72..4bb85b8 100644
--- a/Map Data/BlackthornGym.yml	
+++ b/Map Data/BlackthornGym.yml	
@@ -106,7 +106,7 @@ Location:
                         TrainerList: 
                         Sublocations:
                 WarpReqs:
-                    - Blackthorn Gym Boulders
+                    - Blackthorn Gym Boulders Room
             
             -
                 Name: Blackthorn Gym 1F Middle
diff --git a/Map Data/FuschiaGym.yml b/Map Data/FuschiaGym.yml
index 672102d..97b0aee 100644
--- a/Map Data/FuschiaGym.yml	
+++ b/Map Data/FuschiaGym.yml	
@@ -20,7 +20,7 @@ Location:
             - LASS 3
             - JANINE 1
         HintName: Fuschia
-        WarpReqs: Fuschia Gym
+        WarpReqs: Fuchsia Gym
         Sublocations:
             -
                 Name: Janine TM
diff --git a/Map Data/LakeOfRage.yml b/Map Data/LakeOfRage.yml
index dc1c789..709abe1 100644
--- a/Map Data/LakeOfRage.yml	
+++ b/Map Data/LakeOfRage.yml	
@@ -13,7 +13,8 @@ Location:
         Code:
         Text:
         AREALV:
-        TrainerList: 
+        TrainerList:
+        WarpReqs: Lake Of Rage
         Sublocations:
             -
                 Name: Lake Of Rage Trainers
diff --git a/Map Data/RocketBase.yml b/Map Data/RocketBase.yml
index 3188d97..aaab8ba 100644
--- a/Map Data/RocketBase.yml	
+++ b/Map Data/RocketBase.yml	
@@ -1,6 +1,6 @@
 Location:
       -
-        Name: Rocket Base Entrance
+        Name: Rocket Base Entry
         FileName: MahoganyTown.asm
         Type: Map
         HasPKMN: No
@@ -17,7 +17,7 @@ Location:
         Sublocations:
 
       -
-        Name: Rocket Base Entrance
+        Name: Rocket Base Entry
         FileName: MahoganyTown.asm
         Type: Map
         HasPKMN: No
diff --git a/Map Data/Route10.yml b/Map Data/Route10.yml
index 17b11f7..acc5ba1 100644
--- a/Map Data/Route10.yml	
+++ b/Map Data/Route10.yml	
@@ -92,6 +92,7 @@ Location:
         WildTableList:
         LocationReqs:
         FlagReqs:
+            - Warps
         ItemReqs:
         FlagsSet:
         ReachableReqs:
@@ -99,7 +100,7 @@ Location:
         Text:
         TrainerList:
         Sublocations:
-        WarpReqs: Power Plant
+        WarpReqs: Power Plant Building
 
     -
         Name: Route 10
diff --git a/Map Data/Route26.yml b/Map Data/Route26.yml
index df0bb25..cac7015 100644
--- a/Map Data/Route26.yml	
+++ b/Map Data/Route26.yml	
@@ -42,7 +42,8 @@ Location:
         ReachableReqs:
         Code:
         Text:
-        TrainerList: 
+        TrainerList:
+        WarpReqs: Route 26
         Sublocations:
     -
         Name: Route 26 Max Elixer
diff --git a/Map Data/Route31.yml b/Map Data/Route31.yml
index aa066e5..109d0f3 100644
--- a/Map Data/Route31.yml	
+++ b/Map Data/Route31.yml	
@@ -13,7 +13,8 @@ Location:
         ReachableReqs:
         Code:
         Text:
-        TrainerList: 
+        TrainerList:
+        WarpReqs: Route 31
         Sublocations:
             -
                 Name: Route 31 Potion
diff --git a/Map Data/Route35.yml b/Map Data/Route35.yml
index 69936d2..9a52c37 100644
--- a/Map Data/Route35.yml	
+++ b/Map Data/Route35.yml	
@@ -1,4 +1,23 @@
 Location:
+
+    -
+        Name: Route 35 Entrance
+        FileName: Route35.asm
+        Type: Map
+        HasPKMN: No
+        WildTableList:
+        LocationReqs:
+        FlagReqs:
+            - Warps
+        ItemReqs:
+        FlagsSet:
+        ReachableReqs:
+        Code:
+        Text:
+        TrainerList:
+        WarpReqs: Route 35 Route
+        Sublocations:
+
     -
         Name: Route 35 Entrance
         FileName: Route35.asm
diff --git a/Map Data/Route39.yml b/Map Data/Route39.yml
index ebd5819..05b464b 100644
--- a/Map Data/Route39.yml	
+++ b/Map Data/Route39.yml	
@@ -31,6 +31,25 @@ Location:
         Text:
         TrainerList:
         Sublocations:
+
+    -
+        Name: Route 39 Entrance
+        FileName: Route39.asm
+        Type: Map
+        HasPKMN: No
+        WildTableList:
+        LocationReqs:
+        FlagReqs:
+            - Warps
+        ItemReqs:
+        FlagsSet:
+        ReachableReqs:
+        Code:
+        Text:
+        TrainerList:
+        WarpReqs: Olivine
+        Sublocations:
+
     -
         Name: Route 39 Entrance
         FileName: Route39.asm
diff --git a/Map Data/Route9.yml b/Map Data/Route9.yml
index 6532ca5..44d8c6e 100644
--- a/Map Data/Route9.yml	
+++ b/Map Data/Route9.yml	
@@ -1,4 +1,23 @@
 Location:
+
+    -
+        Name: Route 9 Entrance
+        FileName: Route9.asm
+        Type: Map
+        HasPKMN: No
+        WildTableList:
+        LocationReqs:
+        FlagReqs:
+            - Warps
+        ItemReqs:
+        FlagsSet:
+        ReachableReqs:
+        Code:
+        Text:
+        AREALV: 32
+        TrainerList:
+        WarpReqs: Route 9 Route
+        Sublocations:
     -
         Name: Route 9 Entrance
         FileName: Route9.asm
diff --git a/Map Data/RuinsOfAlph.yml b/Map Data/RuinsOfAlph.yml
index 7f6528f..d677aa8 100644
--- a/Map Data/RuinsOfAlph.yml	
+++ b/Map Data/RuinsOfAlph.yml	
@@ -45,7 +45,8 @@ Location:
         ReachableReqs:
         Code:
         Text:
-        TrainerList: 
+        TrainerList:
+        WarpReqs: Ruins of Alph Main
         Sublocations:
             -
                 Name: Ruins of Alph Trainers
diff --git a/Map Data/UnionCave.yml b/Map Data/UnionCave.yml
index c78063b..c32a469 100644
--- a/Map Data/UnionCave.yml	
+++ b/Map Data/UnionCave.yml	
@@ -29,7 +29,7 @@ Location:
         Text:
         TrainerList:
         HintName: Union Cave
-        WarpReqs: Union Cave
+        WarpReqs: Union Cave Main
         Sublocations:
                 -    
                     Name: Union Cave Floor 1 Trainers
diff --git a/Warp Data/WarpFriendlyNames.tsv b/Warp Data/WarpFriendlyNames.tsv
index 6fab9c6..fbd63c4 100644
--- a/Warp Data/WarpFriendlyNames.tsv	
+++ b/Warp Data/WarpFriendlyNames.tsv	
@@ -32,8 +32,8 @@
 579	BLACKTHORN_DRAGON_SPEECH_HOUSE	1	2	7	BLACKTHORN_CITY	13	21		X	Blackthorn Dragon Speech House	BLACKTHORN_DRAGON_SPEECH_HOUSE Exit
 570	BLACKTHORN_GYM_1F	5	4	17	BLACKTHORN_CITY	18	11		X	Blackthorn Gym 1F Main	BLACKTHORN_GYM_1F Exit
 571	BLACKTHORN_GYM_1F	5	1	7	BLACKTHORN_GYM_2F	1	7	Blackthorn Gym First Stairs Up		Blackthorn Gym 1F Main	Blackthorn Gym First Stairs Up 
-575	BLACKTHORN_GYM_2F	4	1	7	BLACKTHORN_GYM_1F	1	7	Blackthorn Gym First Stairs Down		Blackthorn Gym Boulders	Blackthorn Gym First Stairs Down 
-576	BLACKTHORN_GYM_2F	4	7	9	BLACKTHORN_GYM_1F	7	9	Blackthorn Gym Second Stairs Down		Blackthorn Gym Boulders	Blackthorn Gym Second Stairs Down 
+575	BLACKTHORN_GYM_2F	4	1	7	BLACKTHORN_GYM_1F	1	7	Blackthorn Gym First Stairs Down		Blackthorn Gym Boulders Room	Blackthorn Gym First Stairs Down 
+576	BLACKTHORN_GYM_2F	4	7	9	BLACKTHORN_GYM_1F	7	9	Blackthorn Gym Second Stairs Down		Blackthorn Gym Boulders Room	Blackthorn Gym Second Stairs Down 
 572	BLACKTHORN_GYM_1F	5	7	9	BLACKTHORN_GYM_2F	7	9	Blackthorn Gym Second Stairs Up		Blackthorn Gym Middle	Blackthorn Gym Second Stairs Up 
 127	ROUTE_46	2	7	33	ROUTE_29_ROUTE_46_GATE	4	0	Route 46 to Route 29 Gate	E	Blackthorn Lower	Route 46 to Route 29 Gate Entrance
 128	ROUTE_46	2	14	5	DARK_CAVE_VIOLET_ENTRANCE	35	33	Route 46 Dark Cave	E	Blackthorn Lower Still	Route 46 Dark Cave Entrance
@@ -495,7 +495,7 @@
 832	PLAYERS_HOUSE_2F	1	7	0	PLAYERS_HOUSE_1F	9	0	Players House Down	X	Players House 2F	Players House Down Exit
 831	PLAYERS_HOUSE_1F	2	9	0	PLAYERS_HOUSE_2F	7	0	Players House Up		Players Room	Players House Up 
 220	ROUTE_10_NORTH	2	3	9	POWER_PLANT	2	17		E	Power Entrance	POWER_PLANT Entrance
-597	POWER_PLANT	1	2	17	ROUTE_10_NORTH	3	9		X	Power Plant	POWER_PLANT Exit
+597	POWER_PLANT	1	2	17	ROUTE_10_NORTH	3	9		X	Power Plant Building	POWER_PLANT Exit
 280	RADIO_TOWER_1F	2	2	7	GOLDENROD_CITY	5	15	Goldenrod Radio Tower	X	Radio Tower 1F	Goldenrod Radio Tower Exit
 281	RADIO_TOWER_1F	2	15	0	RADIO_TOWER_2F	15	0	Radio Tower 1F Up		Radio Tower 1F	Radio Tower 1F Up 
 500	OLIVINE_POKECENTER_1F	2	0	7	POKECENTER_2F	0	7	X			X 
@@ -564,10 +564,10 @@
 99	ROUTE_32	3	11	73	ROUTE_32_POKECENTER_1F	3	7		E	Route 32	ROUTE_32_POKECENTER_1F Entrance
 101	ROUTE_32	3	6	79	UNION_CAVE_1F	17	3	Route 32 Union Cave	E	Route 32	Route 32 Union Cave Entrance
 618	ROUTE_32_POKECENTER_1F	1	3	7	ROUTE_32	11	73		X	Route 32 Center	ROUTE_32_POKECENTER_1F Exit
-106	ROUTE_35	2	9	33	ROUTE_35_GOLDENROD_GATE	4	0	Route 35 to Goldenrod Gate	E	Route 35	Route 35 to Goldenrod Gate Entrance
+106	ROUTE_35	2	9	33	ROUTE_35_GOLDENROD_GATE	4	0	Route 35 to Goldenrod Gate	E	Route 35 Route	Route 35 to Goldenrod Gate Entrance
 567	ECRUTEAK_GYM	3	4	14	ECRUTEAK_GYM	2	4	X			X 
 568	ECRUTEAK_GYM	3	2	4	ECRUTEAK_GYM	4	14	X			X 
-107	ROUTE_35	2	3	5	ROUTE_35_NATIONAL_PARK_GATE	3	7	Route 35 to National Park Gate	E	Route 35	Route 35 to National Park Gate Entrance
+107	ROUTE_35	2	3	5	ROUTE_35_NATIONAL_PARK_GATE	3	7	Route 35 to National Park Gate	E	Route 35 Route	Route 35 to National Park Gate Entrance
 108	ROUTE_36	2	18	8	ROUTE_36_NATIONAL_PARK_GATE	9	4	Route 36 to National Park Gate	E	Route 36	Route 36 to National Park Gate Entrance
 120	ROUTE_42	4	28	9	MOUNT_MORTAR_1F_OUTSIDE	17	33	Mortar Entrance Center	E	Route 42 Center	Mortar Entrance Center Entrance
 118	ROUTE_42	4	0	8	ROUTE_42_ECRUTEAK_GATE	9	4	Route 42 to Ecruteak Gate	E	Route 42 West	Route 42 to Ecruteak Gate Entrance
@@ -587,16 +587,16 @@
 884	ROUTE_5_UNDERGROUND_PATH_ENTRANCE	2	4	3	UNDERGROUND_PATH	3	2	Route 5 Underground Stairs		Route 5 Underground	Route 5 Underground Stairs 
 670	ROUTE_6_UNDERGROUND_PATH_ENTRANCE	2	3	7	ROUTE_6	17	3	Route 6 Underground		Route 6 Underground Gate	Route 6 Underground 
 671	ROUTE_6_UNDERGROUND_PATH_ENTRANCE	2	4	3	UNDERGROUND_PATH	3	24	Route 6 Underground Stairs		Route 6 Underground Gate	Route 6 Underground Stairs 
-214	ROUTE_9	1	48	15	ROCK_TUNNEL_1F	15	3	Route 9 Rock Tunnel	E	Route 9	Route 9 Rock Tunnel Entrance
-219	ROUTE_10_NORTH	2	11	1	ROUTE_10_POKECENTER_1F	3	7		E	Route 9	ROUTE_10_POKECENTER_1F Entrance
+214	ROUTE_9	1	48	15	ROCK_TUNNEL_1F	15	3	Route 9 Rock Tunnel	E	Route 9 Route	Route 9 Rock Tunnel Entrance
+219	ROUTE_10_NORTH	2	11	1	ROUTE_10_POKECENTER_1F	3	7		E	Route 9 Route	ROUTE_10_POKECENTER_1F Entrance
 295	RUINS_OF_ALPH_OUTSIDE	10	2	29	RUINS_OF_ALPH_OMANYTE_CHAMBER	3	9		E	Ruins Ledge Middle	RUINS_OF_ALPH_OMANYTE_CHAMBER Entrance
 296	RUINS_OF_ALPH_OUTSIDE	10	16	33	RUINS_OF_ALPH_AERODACTYL_CHAMBER	3	9		E	Ruins Surf	RUINS_OF_ALPH_AERODACTYL_CHAMBER Entrance
-294	RUINS_OF_ALPH_OUTSIDE	10	14	7	RUINS_OF_ALPH_KABUTO_CHAMBER	3	9		E	Ruins of Alph	RUINS_OF_ALPH_KABUTO_CHAMBER Entrance
-297	RUINS_OF_ALPH_OUTSIDE	10	10	13	RUINS_OF_ALPH_INNER_CHAMBER	10	13		E	Ruins of Alph	RUINS_OF_ALPH_INNER_CHAMBER Entrance
-298	RUINS_OF_ALPH_OUTSIDE	10	17	11	RUINS_OF_ALPH_RESEARCH_CENTER	2	7		E	Ruins of Alph	RUINS_OF_ALPH_RESEARCH_CENTER Entrance
+294	RUINS_OF_ALPH_OUTSIDE	10	14	7	RUINS_OF_ALPH_KABUTO_CHAMBER	3	9		E	Ruins of Alph Main	RUINS_OF_ALPH_KABUTO_CHAMBER Entrance
+297	RUINS_OF_ALPH_OUTSIDE	10	10	13	RUINS_OF_ALPH_INNER_CHAMBER	10	13		E	Ruins of Alph Main	RUINS_OF_ALPH_INNER_CHAMBER Entrance
+298	RUINS_OF_ALPH_OUTSIDE	10	17	11	RUINS_OF_ALPH_RESEARCH_CENTER	2	7		E	Ruins of Alph Main	RUINS_OF_ALPH_RESEARCH_CENTER Entrance
 596	ROUTE_10_POKECENTER_2F_BETA	1	0	7	ROUTE_10_POKECENTER_1F	0	7	X			X 
-301	RUINS_OF_ALPH_OUTSIDE	10	7	5	ROUTE_36_RUINS_OF_ALPH_GATE	4	7	Ruins to Route 36 Gate	E	Ruins of Alph	Ruins to Route 36 Gate Entrance
-302	RUINS_OF_ALPH_OUTSIDE	10	13	20	ROUTE_32_RUINS_OF_ALPH_GATE	0	4	Ruins to Route 32 Gate	E	Ruins of Alph	Ruins to Route 32 Gate Entrance
+301	RUINS_OF_ALPH_OUTSIDE	10	7	5	ROUTE_36_RUINS_OF_ALPH_GATE	4	7	Ruins to Route 36 Gate	E	Ruins of Alph Main	Ruins to Route 36 Gate Entrance
+302	RUINS_OF_ALPH_OUTSIDE	10	13	20	ROUTE_32_RUINS_OF_ALPH_GATE	0	4	Ruins to Route 32 Gate	E	Ruins of Alph Main	Ruins to Route 32 Gate Entrance
 293	RUINS_OF_ALPH_OUTSIDE	10	2	17	RUINS_OF_ALPH_HO_OH_CHAMBER	3	9		E	Ruins of Alph Grass	RUINS_OF_ALPH_HO_OH_CHAMBER Entrance
 299	RUINS_OF_ALPH_OUTSIDE	10	6	19	UNION_CAVE_B1F	3	3	Union Cave Ruins Grass	E	Ruins of Alph Grass	Union Cave Ruins Grass Entrance
 315	RUINS_OF_ALPH_INNER_CHAMBER	5	10	13	RUINS_OF_ALPH_OUTSIDE	10	13		X	Ruins of Alph Inner Chamber	RUINS_OF_ALPH_INNER_CHAMBER Exit
@@ -752,15 +752,15 @@
 816	TRAINER_HOUSE_1F	2	2	13	VIRIDIAN_CITY	23	15		X	Trainer House 1F	TRAINER_HOUSE_1F Exit
 817	TRAINER_HOUSE_1F	2	8	2	TRAINER_HOUSE_B1F	9	4	Trainer House Ladder Down		Trainer House 1F	Trainer House Ladder Down 
 818	TRAINER_HOUSE_B1F	1	9	4	TRAINER_HOUSE_1F	8	2	Trainer House 2F Up	X	Trainer House 2F	Trainer House 2F Up Exit
-333	UNION_CAVE_1F	4	5	19	UNION_CAVE_B1F	7	19	Union Cave 1F Down Ladder		Union Cave	Union Cave 1F Down Ladder 
-335	UNION_CAVE_1F	4	17	31	ROUTE_33	11	9	Union Cave Azalea	X	Union Cave	Union Cave Azalea Exit
+333	UNION_CAVE_1F	4	5	19	UNION_CAVE_B1F	7	19	Union Cave 1F Down Ladder		Union Cave Main	Union Cave 1F Down Ladder 
+335	UNION_CAVE_1F	4	17	31	ROUTE_33	11	9	Union Cave Azalea	X	Union Cave Main	Union Cave Azalea Exit
 756	POKECENTER_2F	3	5	0	TRADE_CENTER	4	7	X			X 
 757	POKECENTER_2F	3	9	0	COLOSSEUM	4	7	X			X 
 758	POKECENTER_2F	3	13	2	TIME_CAPSULE	4	7	X			X 
 759	TRADE_CENTER	1	4	7	POKECENTER_2F	5	0	X			X 
 760	COLOSSEUM	1	4	7	POKECENTER_2F	9	0	X			X 
 761	TIME_CAPSULE	1	4	7	POKECENTER_2F	13	2	X			X 
-336	UNION_CAVE_1F	4	17	3	ROUTE_32	6	79	Union Cave Violet	X	Union Cave	Union Cave Violet Exit
+336	UNION_CAVE_1F	4	17	3	ROUTE_32	6	79	Union Cave Violet	X	Union Cave Main	Union Cave Violet Exit
 339	UNION_CAVE_B1F	5	7	19	UNION_CAVE_1F	5	19	Union Cave B1F Up Ladder		Union Cave B1F	Union Cave B1F Up Ladder 
 764	CELADON_DEPT_STORE_1F	3	2	0	CELADON_DEPT_STORE_ELEVATOR	1	3	X			X 
 342	UNION_CAVE_B2F	1	5	3	UNION_CAVE_B1F	17	31	Union Cave Lapras Basement	X	Union Cave Lapras Basement	Union Cave Lapras Basement Exit
