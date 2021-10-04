# Pokemon Crystal Item Randomizer
This is an item (and badge) randomizer for the popular speedchoice mod of Pokemon Crystal. This randomizer supports randomizing all items and badges in the game (TMs, key items, HMs, itemballs, etc...) and can place items in any possible item location in the game. Currently, several modes of randomization are provided by default, including:
  * Key Items - All key items and HMs are randomized. Badges are also randomized, The goal is to defeat Red.
  * Standard - Most item locations are randomized. Badges are also randomized. The goal is to defeat Red.
  * Tricky - Most (plus a few more) item locations and several "flags" which are effectively items are randomized. Badges are also randomized. The goal is to defeat Red.
  * Johto Mode - All item locations in Johto are randomized. Badges are also randomized. The goal is to defeat the Elite 4.
  * TMs + Key Items - All key items, TMs and HMs are randomized. Badges are also randomized, The goal is to defeat Red.
  * Vintage - All game behavior is (mostly) identical to vanilla Pokemon Crystal. Most item locations are randomized. Badges are also randomized. The goal is to defeat Red. 
# Prerequisites to run the randomizer
There is an .EXE version of the randomizer available under the releases page of this repository. If you have already downloaded this, then just run the "PokemonCrystalItemRandomizer.exe" file provided in the zipped folder.
Alternately, the randomizer can be run by installing python with the PyYAML and PyQt packages and then running "RunGUI.py", after you have downloaded the code in this branch.

Note that this randomizer is ONLY compatible with the speedchoice mod of pokemon crystal, which can be obtained from the Pokemon Crystal Cinco Bingo discord page (link not provided due to legal reasons, google is your friend here). Note that if you want to also randomize the pokemon present in the game, you should use the speedchoice compatible version of the Universal Pokemon Randomizer (also available on the Pokemon Crystal Cinco Bingo discord) to randomize the ROM BEFORE you use this randomizer on it. A settings file for the Universal Pokemon Randomizer ("FullItemRandomizer.rnqs") is provided in this repository that can be used for this purpose.

Note that you MUST turn on the "Better Marts" settings in speedchoice when using this randomizer. Failure to do so may cause softlocks related to one of the chambers in ruins of alph.

# How it works
This randomizer shuffles the locations of all items in the game, while also shuffling the locations of all badges in the game. The game will always still be beatable after this shuffling. The modes provided allow for defining customizable rules for how the randomizer logic allocates items, see the "Modes" folder for several examples of these rules. Optional modifiers are also provided for implementing small logic changes, examples can be found in the "Modifiers" folder.

# If you think you found a bug
If you think you have found a bug, please make a post about it on this on the issues page for this project. There are currently no known bugs within this branch apart from those mentioned within the release pages for specific releases.

# If you have a suggestion/idea/way to speed up game/observation about levels that seem wrong/complaint/etc...
Make a post about it under issues, but please indicate in the title of your post that you are not reporting a bug. Alternately, provide feedback or opinions at: https://docs.google.com/forms/d/e/1FAIpQLSdm8cboJjdUr7feqZqxocbN0JXNhZsMwgkhuWj3crkL62uG_A/viewform?usp=pp_url. Posts made in the "crystal-item-rando" channel of the Pokemon Crystal Cinco Bingo discord will also typically be seen and addressed.

# List of changes relative to vanilla crystal
  * Team Rocket taking over the radio tower will not block the following things:
    * Obtaining the radio card
    * Obtaining the item from the flower shop
    * Obtaining the item from Buena
  * The director is always present in the basement, but will not give the player an item until team rocket has actually has attacked.
  * Team Rocket's takeover of the radio tower can be triggered from either Johto or Kanto
    * Note: Team Rocket taking over the Johto radio tower does not affect the radio in Kanto
  * Red will appear in Mt. Silver, even if the Elite Four and Lance have not been beaten yet (can be disabled if desired)
  * The player does not need to return the Mystery Egg to Professor Elm in order to progress the game (can be disabled if desired)
  * The SS Aqua operates every day of the week in both directions between Kanto and Johto
  * The SS Aqua can be ridden in both directions without having beaten the Elite Four and Lance
  * Under a number of settings, the cut tree in Ilex Forest is removed (can be turned on or off as desired).
# Item Locations not randomized (unless you use Tricky settings):
  * Tin Tower and the rainbow wing, because putting the rainbow wing into the randomizer would be overly sadistic as it could then be required to catch all three legendary dogs in order  to beat the game. (NOTE: Tricky settings change this requirement to just defeating Suicune and having the rainbow wing)
  * Ho-oh ruins of alph chamber: Due due to Ho-oh not being reliably obtainable. (NOTE: Tricky settings change this requirement to defeating Ho-Oh on top of Tin Tower)
