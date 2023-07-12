	object_const_def ; object_event constants
	const SILVERCAVEROOM3_RED

SilverCaveRoom3_MapScripts:
	db 0 ; scene scripts

	db 0 ; callbacks

.ckir_BEFORE_RedEncounter::
.ckir_AFTER_RedEncounter::
Red:
	special FadeOutMusic
	faceplayer
	opentext
	writetext RedSeenText
	waitbutton
	closetext
	winlosstext RedWinLossText, RedWinLossText
	loadtrainer RED, RED1
	startbattle
	dontrestartmapmusic
	reloadmapafterbattle
	special FadeOutMusic
	opentext
	writetext RedLeavesText
	waitbutton
	closetext
	special FadeBlackQuickly
	special ReloadSpritesNoPalettes
	disappear SILVERCAVEROOM3_RED
	pause 15
	special FadeInQuickly
	pause 30
	special HealParty
	refreshscreen
	credits
	end

RedSeenText:
.ckir_BEFORE_RED_INTRO::
	text "<……>              "
	line "<……>              "
	done
.ckir_AFTER_RED_INTRO::

RedWinLossText:
	text "…"
	done

RedLeavesText:
	text "<……>"
	line "<……>"
	done

SilverCaveRoom3_MapEvents:
	db 0, 0 ; filler

	db 1 ; warp events
	warp_event  9, 33, SILVER_CAVE_ROOM_2, 2

	db 0 ; coord events

	db 0 ; bg events

	db 1 ; object events
.ckir_BEFORE_object_event_RED::
	object_event  9, 10, SPRITE_RED, SPRITEMOVEDATA_STANDING_UP, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, Red, EVENT_RED_IN_MT_SILVER
.ckir_AFTER_object_event_RED::

