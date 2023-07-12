	object_const_def ; object_event constants
	const GOLDENRODDEPTSTORE5F_CLERK
	const GOLDENRODDEPTSTORE5F_LASS
	const GOLDENRODDEPTSTORE5F_MIKE
	const GOLDENRODDEPTSTORE5F_POKEFAN_M
	const GOLDENRODDEPTSTORE5F_CARRIE
	const GOLDENRODDEPTSTORE5F_RECEPTIONIST

GoldenrodDeptStore5F_MapScripts:
	db 0 ; scene scripts

	db 1 ; callbacks
	callback MAPCALLBACK_OBJECTS, .CheckIfSunday

.CheckIfSunday:
	readvar VAR_WEEKDAY
.ckir_BEFORE_timed_events_DEPTSTORE5F1::
	ifnotequal 10, .yes
.ckir_AFTER_timed_events_DEPTSTORE5F1::
	disappear GOLDENRODDEPTSTORE5F_RECEPTIONIST
	return

.ckir_BEFORE_timed_events_DEPTSTORE5F1_yes::
.yes
.ckir_AFTER_timed_events_DEPTSTORE5F1_yes::
	appear GOLDENRODDEPTSTORE5F_RECEPTIONIST
	return

GoldenrodDeptStore5FClerkScript:
	readvar VAR_WEEKDAY
.ckir_BEFORE_DEPTSTORECheckFullScript::
	ifnotequal 10, GoldenrodDeptStore5FClerkFullShopScript
.ckir_AFTER_DEPTSTORECheckFullScript::
	faceplayer
	opentext
	goldenrodmart5f
	closetext
	end

.ckir_BEFORE_DEPTSTORE5FClerkFullShopScript::
.ckir_AFTER_DEPTSTORE5FClerkFullShopScript::
GoldenrodDeptStore5FClerkFullShopScript:
	faceplayer
	opentext
	pokemart MARTTYPE_STANDARD, MART_GOLDENROD_5F_TM02_08_12
	closetext
	end

GoldenrodDeptStore5FReceptionistScript:
	faceplayer
	opentext
	readvar VAR_WEEKDAY
.ckir_BEFORE_timed_events_DEPTSTORE5F2::
	ifequal 10, .EventIsOver
.ckir_AFTER_timed_events_DEPTSTORE5F2::
	checkflag ENGINE_GOLDENROD_DEPT_STORE_TM27_RETURN
	iftrue .EventIsOver
	special GetFirstPokemonHappiness
	writetext GoldenrodDeptStore5FReceptionistOhYourMonDotDotDotText
	promptbutton
.ckir_BEFORE_timed_events_DEPTSTORE5F3::
	ifgreater 0, .VeryHappy
.ckir_AFTER_timed_events_DEPTSTORE5F3::
	ifgreater 50 - 1, .SomewhatHappy
	sjump .NotVeryHappy

.ckir_BEFORE_timed_events_DEPTSTORE5F3_VeryHappy::
.VeryHappy:
.ckir_AFTER_timed_events_DEPTSTORE5F3_VeryHappy::
	writetext GoldenrodDeptStore5FReceptionistThisMoveShouldBePerfectText
	promptbutton
	checkevent EVENT_GOT_TM27
	iftrue .Onwards27
	verbosegiveitem TM_RETURN
	iffalse .Onwards27
	setevent EVENT_GOT_TM27
.Onwards27
	checkitemrando
	iftrue .NotVeryHappy
	jump .Complete

.SomewhatHappy:
	writetext GoldenrodDeptStore5FReceptionistItsAdorableText
	waitbutton
	closetext
	end

.ckir_BEFORE_timed_events_DEPTSTORE5F4_NotVeryHappy::
.NotVeryHappy:
.ckir_AFTER_timed_events_DEPTSTORE5F4_NotVeryHappy::
	writetext GoldenrodDeptStore5FReceptionistItLooksEvilHowAboutThisTMText
	promptbutton
	checkevent EVENT_GOT_TM21
	iftrue .Onwards21
	verbosegiveitem TM_FRUSTRATION
	iffalse .Onwards21
	setevent EVENT_GOT_TM21
.Onwards21
	checkitemrando
	iffalse .Complete
	checkevent EVENT_GOT_TM27
	iffalse .EventIsOver
	checkevent EVENT_GOT_TM21
	iffalse .EventIsOver
.Complete
    setflag ENGINE_GOLDENROD_DEPT_STORE_TM27_RETURN
    clearevent EVENT_GOT_TM27
    clearevent EVENT_GOT_TM21

.ckir_BEFORE_timed_events_DEPTSTORE5_EventIsOver::
.EventIsOver
.ckir_AFTER_timed_events_DEPTSTORE5_EventIsOver::
    writetext GoldenrodDeptStore5FReceptionistThereAreTMsPerfectForMonText
    waitbutton

.Done:
    closetext
    end

Carrie:
	faceplayer
	opentext
	special GameboyCheck
	ifnotequal GBCHECK_CGB, .NotGBC ; This is a dummy check from Gold/Silver
	writetext GoldenrodDeptStore5FCarrieMysteryGiftExplanationText
	waitbutton
	closetext
	special UnlockMysteryGift
	end

.NotGBC:
	writetext GoldenrodDeptStore5FCarrieMysteryGiftRequiresGBCText
	waitbutton
	closetext
	end

GoldenrodDeptStore5FLassScript:
	jumptextfaceplayer GoldenrodDeptStore5FLassText

Mike:
	faceplayer
	opentext
	trade NPC_TRADE_MIKE
	waitbutton
	closetext
	end

GoldenrodDeptStore5FPokefanMScript:
	jumptextfaceplayer GoldenrodDeptStore5FPokefanMText

GoldenrodDeptStore5FDirectory:
	jumptext GoldenrodDeptStore5FDirectoryText

GoldenrodDeptStore5FElevatorButton:
	jumpstd ElevatorButtonScript

GoldenrodDeptStore5FReceptionistOhYourMonDotDotDotText:
	text "Hello. Oh, your"
	line "#MON…"
	done

GoldenrodDeptStore5FReceptionistThisMoveShouldBePerfectText:
	text "It's very attached"
	line "to you."

	para "This move should"
	line "be perfect for a"
	cont "pair like you."
	done

GoldenrodDeptStore5FReceptionistItsAdorableText:
	text "It's adorable!"

	para "You should teach"
	line "it good TM moves."
	done

GoldenrodDeptStore5FReceptionistItLooksEvilHowAboutThisTMText:
	text "It looks evil. How"
	line "about this TM for"
	cont "it?"
	done

GoldenrodDeptStore5FReceptionistThereAreTMsPerfectForMonText:
	text "There are sure to"
	line "be TMs that are"

	para "just perfect for"
	line "your #MON."
	done

GoldenrodDeptStore5FCarrieMysteryGiftExplanationText:
	text "MYSTERY GIFT."

	para "With just a"
	line "little beep, you"
	cont "get a gift."
	done

GoldenrodDeptStore5FCarrieMysteryGiftRequiresGBCText:
	text "The MYSTERY GIFT"
	line "option requires a"
	cont "Game Boy Color."
	done

GoldenrodDeptStore5FLassText:
	text "On Sundays, a lady"
	line "comes to check out"
	cont "#MON."

	para "She even gives"
	line "away TMs!"
	done

GoldenrodDeptStore5FPokefanMText:
	text "You can't rename a"
	line "#MON you get in"
	cont "a trade."

	para "The name is a re-"
	line "flection of the"
	para "original trainer's"
	line "feelings for it."
	done

GoldenrodDeptStore5FDirectoryText:
	text "Customize Your"
	line "#MON"

	para "5F TM CORNER"
	done

GoldenrodDeptStore5F_MapEvents:
	db 0, 0 ; filler

	db 3 ; warp events
	warp_event 12,  0, GOLDENROD_DEPT_STORE_4F, 1
	warp_event 15,  0, GOLDENROD_DEPT_STORE_6F, 1
	warp_event  2,  0, GOLDENROD_DEPT_STORE_ELEVATOR, 1
	db 0 ; coord events

	db 2 ; bg events
	bg_event 14,  0, BGEVENT_READ, GoldenrodDeptStore5FDirectory
	bg_event  3,  0, BGEVENT_READ, GoldenrodDeptStore5FElevatorButton

	db 6 ; object events
	object_event  8,  5, SPRITE_CLERK, SPRITEMOVEDATA_STANDING_UP, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, GoldenrodDeptStore5FClerkScript, -1
	object_event  3,  6, SPRITE_LASS, SPRITEMOVEDATA_WANDER, 1, 1, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, GoldenrodDeptStore5FLassScript, -1
	object_event  6,  3, SPRITE_COOLTRAINER_M, SPRITEMOVEDATA_SPINRANDOM_SLOW, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, Mike, -1
	object_event 13,  5, SPRITE_POKEFAN_M, SPRITEMOVEDATA_WANDER, 2, 2, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, GoldenrodDeptStore5FPokefanMScript, -1
	object_event  9,  1, SPRITE_TWIN, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_GREEN, OBJECTTYPE_SCRIPT, 0, Carrie, -1
	object_event  7,  5, SPRITE_RECEPTIONIST, SPRITEMOVEDATA_STANDING_UP, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, GoldenrodDeptStore5FReceptionistScript, EVENT_GOLDENROD_DEPT_STORE_5F_HAPPINESS_EVENT_LADY