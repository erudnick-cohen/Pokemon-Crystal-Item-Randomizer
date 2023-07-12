rm -r build
rm -r dist

pyuic5.exe QTGUIDesign.ui -o RandomizerGUI.py
if errorlevel 1 (
   echo Failure Reason Given is %errorlevel%
   exit /b %errorlevel%
)

pyinstaller RunGUIBuild.spec
if errorlevel 1 (
   echo Failure Reason Given is %errorlevel%
   exit /b %errorlevel%
)

rm "Warp Data/warp-output.tsv"
rm -r "dist/Pokemon Crystal Item Randomizer"
rename "dist/RunGUI" "Pokemon Crystal Item Randomizer"
echo F|Xcopy "crystal-speedchoice-label-details.json" "dist/Pokemon Crystal Item Randomizer/crystal-speedchoice-label-details.json" /i /y
echo F|Xcopy "ItemValues.csv" "dist/Pokemon Crystal Item Randomizer/ItemValues.csv" /i /y
echo F|Xcopy "AddItemValues.csv" "dist/Pokemon Crystal Item Randomizer/AddItemValues.csv" /i /y
echo F|Xcopy "FlagValues.csv" "dist/Pokemon Crystal Item Randomizer/FlagValues.csv" /i /y
echo F|Xcopy "BadgeData.yml" "dist/Pokemon Crystal Item Randomizer/BadgeData.yml" /i /y
echo F|Xcopy "FullItemRandomizer.rnqs" "dist/Pokemon Crystal Item Randomizer/FullItemRandomizer.rnqs" /i /y
echo F|Xcopy "README.md" "dist/Pokemon Crystal Item Randomizer/README.txt" /i /y
echo F|Xcopy "DefaultRandomizerConfig.yml" "dist/Pokemon Crystal Item Randomizer/RandomizerConfig.yml" /i /y
echo F|Xcopy "ItemDescriptions.json" "dist/Pokemon Crystal Item Randomizer/ItemDescriptions.json" /i /y

::echo F|Xcopy "Config/SignData.json" "dist/Pokemon Crystal Item Randomizer/ItemDescriptions.json" /i /y

Xcopy "Data" "dist/Pokemon Crystal Item Randomizer/Data" /i /y
Xcopy "Warp Data" "dist/Pokemon Crystal Item Randomizer/Warp Data" /i /y
Xcopy "Gym Data" "dist/Pokemon Crystal Item Randomizer/Gym Data" /i /y
Xcopy "ItemData" "dist/Pokemon Crystal Item Randomizer/ItemData" /i /y
Xcopy "Map Data" "dist/Pokemon Crystal Item Randomizer/Map Data" /i /y
Xcopy "Config" "dist/Pokemon Crystal Item Randomizer/Config" /i /y
Xcopy "Modes" "dist/Pokemon Crystal Item Randomizer/Modes" /i /y
Xcopy "Modifiers" "dist/Pokemon Crystal Item Randomizer/Modifiers" /s /i /y
Xcopy "Patches" "dist/Pokemon Crystal Item Randomizer/Patches" /i /y
Xcopy "Special Pokemon Locations" "dist/Pokemon Crystal Item Randomizer/Special Pokemon Locations" /i /y
Xcopy "TrainerData" "dist/Pokemon Crystal Item Randomizer/TrainerData" /i /y
Xcopy "Wild Data" "dist/Pokemon Crystal Item Randomizer/Wild Data" /i /y
Xcopy "Packs" "dist/Pokemon Crystal Item Randomizer/Packs" /i /y
