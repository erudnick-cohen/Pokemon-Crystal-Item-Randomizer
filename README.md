# Pokemon Crystal Item Randomizer (speedchoice branch)
This is an item (and badge) randomizer for the popular speedchoice mod of pokemon crystal. This randomizer supports randomizing all items and badges in the game (TMs, key items, HMs, itemballs, etc...) and can place items in any possible item location in the game. Currently, 3 modes of randomization are provided by default
  * Standard - All items locations are randomized. Badges are also randomized. The goal is to defeat red.
  * Johto Mode - All item locations in Johto are randomized. Badges are also randomized. The goal is to defeat the Elite 4.
  * TMs + Key Items - An expanded version of the popular Crystal Key Item Randomizer. This mode "mostly" contains item locations that should be familiar for anyone who has played Crystal Cinco Bingo and/or the crystal key item randomizer. This mode randomizes all item locations that would contain a TM, Key Item or HM. Badges are also randomized. The goal is to defeat red.

# Prerequisites to run the randomizer
There is an .EXE version of the randomizer available under the releases page of this repository. If you have already downloaded this, then just run the "PokemonCrystalItemRandomize.exe" file provided in the zipped folder.
Alternately, the randomizer can be run by installing python with the PyYAML and PyQt packages and then running "RunGUI.py", after you have downloaded the code in this branch.

Note that this randomizer is ONLY compatible with the speedchoice mod of pokemon crystal, which can be obtained from the Pokemon Crystal Cinco Bingo discord page (link not provided due to legal reasons, google is your friend here). Note that if you want to also randomize the pokemon present in the game, you should use the speedchoice compatible version of the Universal Pokemon Randomizer (also available on the Pokemon Crystal Cinco Bingo discord) to randomize the ROM BEFORE you use this randomizer on it. A settings file for the Universal Pokemon Randomizer ("FullItemRandomizer.rnqs") is provided in this repository that can be used for this purpose.

Note that you MUST turn on the "Better Marts" settings in speedchoice when using this randomizer. Failure to do so may cause softlocks related to one of the chambers in ruins of alph.

# How it works
This randomizer shuffles the locations of all items in the game, while also shuffling the locations of all badges in the game. The game will always still be beatable after this shuffling. It also (optionally) can rescale trainer (and wild pokemon) levels to prevent situations where the player might end up fighting stronger trainers early (or if the player wants to buff up Crystal's pretty terrible wild pokemon levels). The modes provided allow for defining customizable rules for how the randomizer logic allocates items, see the "Modes" folder for several examples of these rules. Optional modifiers are also provided for implementing small logic changes, examples can be found in the "Modifiers" folder.

# If you think you found a bug
If you think you have found a bug, please make a post about it on this on the issues page for this project. There are currently no known bugs within this branch. Note that this branch does not randomize text (see the master branch for the version of the randomizer that does).

# If you have a suggestion/idea/way to speed up game/observation about levels that seem wrong/complaint/etc...
Make a post about it under issues, but please indicate in the title of your post that you are not reporting a bug. Alternately, provide feedback or opinions at: https://docs.google.com/forms/d/e/1FAIpQLSdm8cboJjdUr7feqZqxocbN0JXNhZsMwgkhuWj3crkL62uG_A/viewform?usp=pp_url

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
# Item Locations not randomized:
  * Tin Tower and the rainbow wing, because putting the rainbow wing into the randomizer would be overly sadistic as it could then be required to catch all three legendary dogs in order  to beat the game.
  * Ho-oh ruins of alph chamber: Due due to Ho-oh not being reliably obtainable.
  * The metal coat given to the player on the SS Aqua, due to a weird situation where it has two separate instances of being given
