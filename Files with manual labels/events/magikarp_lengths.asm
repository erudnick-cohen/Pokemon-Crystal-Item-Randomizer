MagikarpLengths:
; [wMagikarpLength] = z * 100 + (bc - x) / y
; First argument is the bc threshold as well as x.
; Second argument is y.
; In reality, due to the bug at .BCLessThanDE,
; the threshold is determined by only register b.
.ckir_BEFORE_MAGIKARPLENGTH::
	dwb   1, 1 ; not used unless the bug is fixed
	dwb   2, 2
	dwb   3, 4
	dwb  4, 20
	dwb  5, 50
	dwb 6, 100
	dwb 7, 150
	dwb 8, 150
	dwb 32710, 100
	dwb 62710, 50
	dwb 64710, 20
	dwb 65210, 5
	dwb 65410, 2
	dwb 65510, 1 ; not used
.ckir_AFTER_MAGIKARPLENGTH::