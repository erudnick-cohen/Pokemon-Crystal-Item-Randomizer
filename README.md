# Pokemon Crystal Item Randomizer
This is an item randomizer for pokemon crystal. Unlike many existing pokemon randomizers, this randomizer not only randomizes what pokemon appear, but also the item locations of the regular(non-hidden) and key items in the game.

# Prequisites to run the randomizer
In order to run this item randomizer you need the ability to build pokecrystal (https://github.com/pret/pokecrystal), instructions on how to do this can be found in the README for pokecrystal. Additionally, you need python installed with the PyYAML package.

# How to run the randomizer
First, from the top level of this repo, run:
```
py TestRandomizationKanto.py
```
Alternately, if one wants to randomize the game with the goal of only staying in Johto, run:
```
py TestRandomizationSimple.py
Be aware that when using TestRandomizationSimple.py, the randomizer will occaisionally fail to produce a valid seed due to an "unsolvable" allocation of gyms, this should be checked for when using this file
```
If you don't want to see the solution to the generated seed, it is reccommended you pipe the output of these files to a file (ex. run "py TestRandomizationKanto.py > output.log")
After this completes move to the RandomizerRom directory that will have been created and run:
```
make
```
Once the build finishes, the randomized rom of pokemon crystal will be located in the RandomizerRom folder, with the file being titled "pokecrystal.gbc".

# How it works
This randomizer uses YAML files to represent most of the locations in pokemon crystal. It allocates items in a random manner while simultaneously rebalancing trainer levels to account for the fact that the player may be able(and may need to) to access areas that might normally contain trainers with much higher levels than the player's pokemon. Wild pokemon are randomized so that pokemon encountered can always learn the same HMs as what they replace, with the exception of Fly and only up to the point at which the player encounters areas where they need use an HM to progress. Pokemon are randomized within a range of their total base stats in order to prevent potentially unwinnable situations. All "boss" pokemon (pokemon used by a trainer that have actual movesets programmed) are instead shuffled between the trainers that normally have them with a the same restriction applied to base stats.

# If you think you found a bug
If you think you have found a bug, please make a post about it on this on the issues page for this project. The following bugs are known to exist in the current implementation of the randomizer:
1. Some text occaisionally pushes outside the text box of NPCs

# If you have a suggestion/idea/way to speed up game/observation about levels that seem wrong/complaint/etc...
Make a post about it under issues, but please indicate in the title of your post that you are not reporting a bug

# List of changes relative to vanilla crystal
  * Fast text speed is instant text speed, medium text speed is fast text speed, slow text speed is medium text speed
  * Team Rocket taking over the radio tower will not block the following things:
    * Obtaining the radio card
    * Obtaining the item from the flower shop
    * Obtaining the item from Buena
  * The fake director does not need to be fought before clearing Team Rocket from the radio tower, however he remains in the directors office afterwards as he has an item
  * The director will remain in the basement even after Team Rocket is cleared(and is there before it as well), however he will not give the player an item until team rocket actually has attacked
  * Team Rocket's takeover of the radio tower can be triggered from either Johto or Kanto
    * Note: Team Rocket taking over the Johto radio tower does not affect the radio in Kanto
  * Red will appear in Mt. Silver, even if the Elite Four and Lance have not been beaten yet
  * The SS Aqua operates every day of the week in both directions bewteen Kanto and Johto
  * The SS Aqua can be ridden in both directions without having beaten the Elite Four and Lance
# Item Locations not randomized:
  * Tin Tower and the rainbow wing, because putting the rainbow wing into the randomizer would be overly sadistic as it could then be required to catch all three legendary dogs in order  to beat the game.
  * Water stone and ho-oh ruins of alph chambers: Due to the player being able to softlock themselves by using water stones and due to Ho-oh not being reliably obtainable.
  * Hidden item locations, due to there being too many of them and the fact that they aren't actually visible. There is one exception to this rule, which is the machine part's location, as it is normally a key item's location.