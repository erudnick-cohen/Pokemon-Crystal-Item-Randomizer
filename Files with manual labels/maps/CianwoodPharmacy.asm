	object_const_def ; object_event constants
	const CIANWOODPHARMACY_PHARMACIST

CianwoodPharmacy_MapScripts:
	db 1 ; scene scripts
	scene_script .DummyScene

	db 0 ; callbacks

.DummyScene:
	end


CianwoodPharmacist:
	faceplayer
	opentext
	checkevent EVENT_GOT_SECRETPOTION_FROM_PHARMACY
	iftrue .Mart
	checkevent EVENT_JASMINE_EXPLAINED_AMPHYS_SICKNESS
	iffalse .Mart
	writetext PharmacistGiveSecretpotionText
	promptbutton
	verbosegiveitem SECRETPOTION
	iffalse .SkipSecretPotion
	setevent EVENT_GOT_SECRETPOTION_FROM_PHARMACY
.SkipSecretPotion
	writetext PharmacistDescribeSecretpotionText
	waitbutton
	sjump .CheckShopsanity
	end

.CheckShopsanity
	checkevent EVENT_JASMINE_EXPLAINED_AMPHYS_SICKNESS
.ckir_BEFORE_CIANWOODPHARMACY_SHOPSANITY_CHECK::
	iftrue .Mart
.ckir_AFTER_CIANWOODPHARMACY_SHOPSANITY_CHECK::
	closetext
	end


.ckir_BEFORE_CIANWOODPHARMACY_MART::
.ckir_AFTER_CIANWOODPHARMACY_MART::
.Mart:
	pokemart MARTTYPE_PHARMACY, MART_CIANWOOD
	closetext
	end

CianwoodPharmacyBookshelf:
	jumpstd DifficultBookshelfScript

PharmacistGiveSecretpotionText:
	text "Your #MON ap-"
	line "pear to be fine."

	para "Is something wor- "
	line "rying you?"

	para "…"

	para "The LIGHTHOUSE"
	line "#MON is in"
	cont "trouble?"

	para "I got it!"

	para "This ought to do"
	line "the trick."
	done

ReceivedSecretpotionText:
	text "<PLAYER> received"
	line "SECRETPOTION."
	done

PharmacistDescribeSecretpotionText:
	text "My SECRETPOTION is"
	line "a tad too strong."

	para "I only offer it in"
	line "an emergency."
	done

CianwoodPharmacy_MapEvents:
	db 0, 0 ; filler

	db 2 ; warp events
	warp_event  2,  7, CIANWOOD_CITY, 4
	warp_event  3,  7, CIANWOOD_CITY, 4

	db 0 ; coord events

	db 2 ; bg events
	bg_event  0,  1, BGEVENT_READ, CianwoodPharmacyBookshelf
	bg_event  1,  1, BGEVENT_READ, CianwoodPharmacyBookshelf

	db 1 ; object events
	object_event  2,  3, SPRITE_PHARMACIST, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, CianwoodPharmacist, -1