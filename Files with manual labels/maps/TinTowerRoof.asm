	object_const_def ; object_event constants
	const TINTOWERROOF_HO_OH

TinTowerRoof_MapScripts:
	db 0 ; scene scripts

	db 1 ; callbacks
	callback MAPCALLBACK_OBJECTS, .HoOh

.HoOh:
	checkitemrando
	iffalse .NoE4Check
	checkhoohchambernerfed
	iftrue .NoE4Check
	checkevent EVENT_BEAT_ELITE_FOUR
.ckir_BEFORE_ALWAYSHOOHSETTING1::
	iffalse .NoAppear
.ckir_AFTER_ALWAYSHOOHSETTING1::

.NoE4Check:
	checkevent EVENT_FOUGHT_HO_OH
	iftrue .NoAppear
	checkitem RAINBOW_WING
	iftrue .Appear
.ckir_BEFORE_ALWAYSHOOHSETTING2::
	sjump .NoAppear
.ckir_AFTER_ALWAYSHOOHSETTING2::

.ckir_BEFORE_ALWAYSHOOHSETTING3::
.Appear:
.ckir_AFTER_ALWAYSHOOHSETTING3::
	appear TINTOWERROOF_HO_OH
	return

.ckir_BEFORE_ALWAYSHOOHSETTING4::
.NoAppear:
.ckir_AFTER_ALWAYSHOOHSETTING4::
	disappear TINTOWERROOF_HO_OH
	return

TinTowerHoOh:
	faceplayer
	opentext
	writetext HoOhText
Randomizer_HoOhCry::
	cry HO_OH
	pause 15
	closetext
	setevent EVENT_FOUGHT_HO_OH
	loadvar VAR_BATTLETYPE, BATTLETYPE_FORCEITEM
Randomizer_HoOhSpecies::
.ckir_BEFORE_HOOHENCOUNTER::
	loadwildmon HO_OH, 60
.ckir_AFTER_HOOHENCOUNTER::
	startbattle
	disappear TINTOWERROOF_HO_OH
	reloadmapafterbattle
	setevent EVENT_SET_WHEN_FOUGHT_HO_OH
	end

HoOhText:
	text "Shaoooh!"
	done

TinTowerRoof_MapEvents:
	db 0, 0 ; filler

	db 1 ; warp events
	warp_event  9, 13, TIN_TOWER_9F, 4

	db 0 ; coord events

	db 0 ; bg events

	db 1 ; object events
	object_event  9,  5, SPRITE_HO_OH, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, TinTowerHoOh, EVENT_TIN_TOWER_ROOF_HO_OH
