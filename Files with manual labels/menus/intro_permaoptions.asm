
VersionNumberText::
        db "v7.4.10@"

SpeedchoiceVersion:
; Speedchoice Major Version
.ckir_BEFORE_MajorVersionNumber::
db 7
.ckir_AFTER_MajorVersionNumber::

; Speedchoice Minor Version
.ckir_BEFORE_MinorVersionNumber::
db 4
.ckir_AFTER_MinorVersionNumber::

; Speedchoice Revision
.ckir_BEFORE_RevisionVersionNumber::
db 10
.ckir_AFTER_RevisionVersionNumber::

IntroPermaOptions::
        xor a
        ld hl, wPermanentOptions
rept NUM_PERMAOPTIONS_BYTES
        ld [hli], a
endr
        ld a, [HOLD_TO_MASH_ADDRESS]
        push af
        and $ff ^ HOLD_TO_MASH_VAL
        ld [HOLD_TO_MASH_ADDRESS], a
        ld hl, PleaseSetOptionsText
        call PrintText
        pop af
        ld [HOLD_TO_MASH_ADDRESS], a
        xor a
        ld [wRandomizedMovesStatus], a
        ld a, "@"
        ld [wPlayerName], a
        ld hl, wPlayerGender
        set 0, [hl]
.setOptions
        callba PermaOptionsMenu
        call ClearTilemap
        call PrintPermaOptionsToScreen
        ld hl, AreOptionsAcceptableText
        call PrintText
        lb bc, 14, 7
        call PlaceYesNoBox
        ld a, [wMenuCursorY]
        dec a
        jr nz, .setOptions
; setup stats now
        ld a, 1
        ldh [hStatsDisabled], a
        ld a, BANK(sStatsStart)
        call OpenSRAM
        xor a
        ld hl, sStatsStart
        ld bc, sStatsEnd - sStatsStart
        call ByteFill
        call CloseSRAM
        ldh [hStatsDisabled], a ; still 0 from above
        ret

PrintPermaOptionsToScreen::
        coord hl, 13, 0
        ld de, VersionNumberText
        call PlaceString
        ld a, [ROCKETLESS_ADDRESS] ; spinners, max range, nerf hms, better enc slots
        ld b, a
; rocketless
        coord hl, 1, 1
        bit ROCKETLESS, b
        ld de, NormalRocketsText
        jr z, .placeRocketSetting
        ld de, RocketlessText
.placeRocketSetting
        call PlaceStringIncHL
; spinners
        ld a, b
        and SPINNERS_MASK
        push hl
        ld hl, .SpinnerOptionsStrings
        add l
        ld l, a
        jr nc, .loadPtr
        inc h
.loadPtr
        ld a, [hli]
        ld d, [hl]
        ld e, a
        pop hl
        call PlaceStringIncHL
; vision
        bit MAX_RANGE, b
        ld de, NormalVisionText
        jr z, .placeVisionSetting
        ld de, MaxVisionText
.placeVisionSetting
        call PlaceStringIncHL
; hms
        ld a, [wRandomizedMovesStatus]
        cp 2 ; randomized
        jr nz, .normalTreatment
        ld de, RandomizedMovesText
        jr .placeHMSetting
.normalTreatment
        bit NERF_HMS, b
        ld de, NormalHMsText
        jr z, .placeHMSetting
        ld de, NerfedHMsText
.placeHMSetting
        call PlaceStringIncHL
; encs
        bit BETTER_ENC_SLOTS, b
        ld de, NormalEncountersText
        jr z, .placeEncSetting
        ld de, BetterEncountersText
.placeEncSetting
        call PlaceStringIncHL
; exp
        ld a, b
        and EXP_FORMULA_MASK
        rlca
        rlca
        add a
        push hl
        ld hl, .ExpFormulaOptionsStrings
        add l
        ld l, a
        jr nc, .loadPtrExp
        inc h
.loadPtrExp
        ld a, [hli]
        ld d, [hl]
        ld e, a
        pop hl
        call PlaceStringIncHL
; tin tower
        ld a, [EASY_TIN_TOWER_ADDRESS]
        ld b, a
        bit EASY_TIN_TOWER, b
        ld de, NormalTinTowerText
        jr z, .placeTowerSetting
        ld de, EasyTinTowerText
.placeTowerSetting
        call PlaceStringIncHL
; marts
        bit BETTER_MARTS, b
        ld de, NormalMartsText
        jr z, .placeMartSetting
        ld de, BetterMartsText
.placeMartSetting
        call PlaceStringIncHL
; wilds
        bit EVOLVED_EARLY_WILDS, b
        ld de, NormalWildsText
        jr z, .placeWildsSetting
        ld de, BetterWildsText
.placeWildsSetting
        call PlaceStringIncHL
; kanto
        bit EARLY_KANTO, b
        ld de, NormalKantoText
        jr z, .placeKantoSetting
        ld de, EarlyKantoText
.placeKantoSetting
        call PlaceStringIncHL
; checkvalue stuff
        coord hl, 1, 11
        ld [hl], "C"
        inc hl
        ld [hl], "V"
        inc hl
        ld [hl], "<COLON>"
        inc hl
        inc hl
        push hl
        ld hl, CheckValue
        ld de, wBuffer1
        ld bc, 4
        call CopyBytes
bnum = 0
        rept NUM_PERMAOPTIONS_BYTES
bnum = bnum + 1
if bnum % 4 == 1
        ld hl, wBuffer1
endc
        ld a, [wPermanentOptions + bnum - 1]
        xor [hl]
        ld [hli], a
        endr
        pop hl
        ld de, wBuffer1
        ld c, 4
.checkValueLoop
        ld a, [de]
        inc de
        call PrintHexByte
        dec c
        jr nz, .checkValueLoop
        ret
.SpinnerOptionsStrings
        dw NormalSpinnersText
        dw NoSpinnersText
        dw SpinnerHellText
        dw SuperSpinnerHellText
.ExpFormulaOptionsStrings
        dw NormalExpText
        dw BWExpText
        dw NoExpText

PlaceStringIncHL::
        push bc
        call PlaceString
        ld bc, SCREEN_WIDTH
        add hl, bc
        pop bc
        ret

PrintHexByte::
; a contains the value to be displayed
        ld b, a
; upper nibble
        swap b
        call .printNibble
        swap b
.printNibble
        ld a, b
        and $0F
        add "0"
        or $80
        ld [hli], a
        ret

SelectedOptionsText::
        db "SELECTED OPTIONS@"
NormalRocketsText::
        db "NORMAL ROCKETS@"
RocketlessText::
        db "ROCKETLESS@"
NormalSpinnersText::
        db "NORMAL SPINNERS@"
NoSpinnersText::
        db "SPINNERLESS@"
SpinnerHellText::
        db "SPINNER HELL@"
SuperSpinnerHellText::
        db "SUPER SPINNER HELL@"
NormalVisionText::
        db "NORMAL VISION@"
MaxVisionText::
        db "MAX VISION@"
NormalHMsText::
        db "NORMAL HMs@"
NerfedHMsText::
        db "NERFED HMs@"
RandomizedMovesText::
        db "RANDOMIZED MOVES@"
NormalEncountersText::
        db "NORMAL ENC SLOTS@"
BetterEncountersText::
        db "BETTER ENC SLOTS@"
NormalExpText::
        db "NORMAL EXP@"
BWExpText::
        db "B/W EXP@"
NoExpText::
        db "NO EXP@"
NormalMartsText::
        db "NORM MARTS@"
BetterMartsText::
        db "GOOD MARTS@"
NormalWildsText::
        db "NORM WILDS@"
BetterWildsText::
        db "GOOD WILDS@"
NormalKantoText::
        db "NORM KANTO@"
EarlyKantoText::
        db "EARLY KANTO@"
NormalTinTowerText::
        db "NORMAL TIN TOWER@"
EasyTinTowerText::
        db "EASY TIN TOWER@"

PleaseSetOptionsText::
        text_jump _PleaseSetOptionsText
        db "@"

AreOptionsAcceptableText::
        text_jump _AreOptionsAcceptableText
        db "@"