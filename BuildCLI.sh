rm -r build
rm -r dist

pyinstaller RunCLIBuild.spec
code=$?
  
if [ $code -ne 0 ]
then
	echo Failure Reason Given is $code
	exit $code
fi

rm "Warp Data/warp-output.tsv"
rm -r "dist/Pokemon Crystal Item Randomizer"
mv "dist/RunCLI" "dist/Pokemon Crystal Item Randomizer"
cp "crystal-speedchoice-label-details.json" "dist/Pokemon Crystal Item Randomizer/crystal-speedchoice-label-details.json"
cp "ItemValues.csv" "dist/Pokemon Crystal Item Randomizer/ItemValues.csv"
cp "AddItemValues.csv" "dist/Pokemon Crystal Item Randomizer/AddItemValues.csv"
cp "FlagValues.csv" "dist/Pokemon Crystal Item Randomizer/FlagValues.csv"
cp "BadgeData.yml" "dist/Pokemon Crystal Item Randomizer/BadgeData.yml"
cp "FullItemRandomizer.rnqs" "dist/Pokemon Crystal Item Randomizer/FullItemRandomizer.rnqs"
cp "README.md" "dist/Pokemon Crystal Item Randomizer/README.txt"
cp "DefaultRandomizerConfig.yml" "dist/Pokemon Crystal Item Randomizer/RandomizerConfig.yml"
cp "ItemDescriptions.json" "dist/Pokemon Crystal Item Randomizer/ItemDescriptions.json"

cp "Config/SignData.json" "dist/Pokemon Crystal Item Randomizer/ItemDescriptions.json"

cp -r "Data" "dist/Pokemon Crystal Item Randomizer/Data"
cp -r "Warp Data" "dist/Pokemon Crystal Item Randomizer/Warp Data"
cp -r "Gym Data" "dist/Pokemon Crystal Item Randomizer/Gym Data"
cp -r "ItemData" "dist/Pokemon Crystal Item Randomizer/ItemData"
cp -r "Map Data" "dist/Pokemon Crystal Item Randomizer/Map Data"
cp -r "Config" "dist/Pokemon Crystal Item Randomizer/Config"
cp -r "Modes" "dist/Pokemon Crystal Item Randomizer/Modes"
cp -r "Modifiers" "dist/Pokemon Crystal Item Randomizer/Modifiers"
cp -r "Patches" "dist/Pokemon Crystal Item Randomizer/Patches"
cp -r "Special Pokemon Locations" "dist/Pokemon Crystal Item Randomizer/Special Pokemon Locations"
cp -r "TrainerData" "dist/Pokemon Crystal Item Randomizer/TrainerData"
cp -r "Wild Data" "dist/Pokemon Crystal Item Randomizer/Wild Data"
cp -r "Packs" "dist/Pokemon Crystal Item Randomizer/Packs"
