# Pokemon Crystal Item Randomizer
This is an item randomizer for pokemon crystal. Unlike many existing pokemon randomizers, this randomizer not only randomizes what pokemon appear, but also the item locations of the regular and key items in the game.

# Prequisites to run the randomizer
In order to run this item randomizer you need the ability to build pokecrystal (https://github.com/pret/pokecrystal), instructions on how to do this can be found in the README for pokecrystal. Additionally, you need python installed with the PyYAML package.

# How to run the randomizer
First, from the top of this repo, run:
'''
py TestRandomizationKanto.py
'''
Alternately, if one wants to randomize the game with the goal of only staying in Johto, run:
'''
py TestRandomizationSimple.py
'''
After this completes move to the RandomizerRom directory that will have been created and run:
'''
make
'''
Once the build finishes, the randomized rom of pokemon crystal will be located in the RandomizerRom folder, with the file being titled "pokecrystal.gbc".

# How it works
This randomizer uses YAML files to represent most of the locations in pokemon crystal. It allocates items in a random manner while simultaneously rebalancing trainer levels to account for the fact that the player may be able(or need to) to access areas that might normally contain trainers with much higher levels than the player. Wild pokemon are randomized so that pokemon encountered can always learn the same HMs as what they replace, with the exception of Fly and only up to the point at which the player encounters areas where they need use an HM to progress. Pokemon are randomized within a range of their total base stats in order to prevent potentially unwinnable situations. All "boss" pokemon (pokemon used by a trainer that have actual movesets programmed) are instead shuffled between the trainers that normally have them.

# If you think you found a bug
If you think you have found a bug, please make a post about it on this on the issues page for this project. The following bugs are known to exist in the current implementation of the randomizer:
1. Some text occaisionally pushes outside the text box of NPCs

# If you have a suggestion/idea/way to speed up game/complaint/ect...
Make a post about it under issues, but please indicate in the title of your post that you are not reporting a bug
