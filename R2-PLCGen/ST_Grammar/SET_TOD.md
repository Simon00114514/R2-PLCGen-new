(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: TIME_DATE
*)
(*@KEY@:DESCRIPTION*)
version 1.5	16. mar 2008
programmer 	hugo
tested by	tobias

creates tod from hour minute and second
(*@KEY@:END_DESCRIPTION*)
FUNCTION SET_TOD:UDINT

(*Group:Default*)


VAR_INPUT
	HOUR :	INT;
	MINUTE :	INT;
	SECOND :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: SET_TOD
IEC_LANGUAGE: ST
*)
set_Tod := _REAL_TO_UDINT(second * 1000.0) + _INT_TO_UDINT(minute) * UDINT#60000 + _INT_TO_UDINT(hour) * UDINT#3600000;

(* revision history

hm		4.aug.2006		rev 1.0
	original version

hm		11. sep 2007	rev 1.1
	changed coding to avoid a compiler warning under twincat.

hm		1. nov 2007	rev 1.2
	changed coding to avoid possible overrun situation on möller ecp4

hm		2. Nov	2007	rev 1.3
	changed dword to DINT in calcualtion to avoid warnings with some compilers

hm		14. mar 2008	rev 1.4
	changed code to avoid rounding problem at last digit of millisecond

hm		16. mar. 2008	rev 1.5
	added type conversions to avoid warning under codesys 3.0
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
