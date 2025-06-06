(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: TIME_DATE
*)
(*@KEY@:DESCRIPTION*)
version 1.7	13. nov. 2009
programmer 	hugo
tested by	oscat

LTIME_TO_UTC calculates UTC (World Time) from a local time LTIME. utc is calculated 
by subtracting Time_Zone_Offset from ltime and if dst it true subtracting an additional hour from ltime.

(*@KEY@:END_DESCRIPTION*)
FUNCTION LTIME_TO_UTC:UDINT

(*Group:Default*)


VAR_INPUT
	LTIME :	UDINT;
	DST :	BOOL;
	TIME_ZONE_OFFSET :	INT;
END_VAR


(*@KEY@: WORKSHEET
NAME: LTIME_TO_UTC
IEC_LANGUAGE: ST
*)
LTIME_TO_UTC := LTIME - _INT_TO_UDINT(TIME_ZONE_OFFSET * 60);
IF DST THEN LTIME_TO_UTC := LTIME_TO_UTC - UDINT#3600; END_IF;

(* revision history
hm 5.7.2007		rev 1.0		
	original version

hm 5.11.2007		rev 1.1
	replaced literal constant with variable because of error in möller ecp4 compiler

hm	12.nov 2007	rev 1.2
	changed Type of time_zone_offset from time to int to allow for time zones with negative offset

hm	8. dec 2007	rev 1.3
	corrected a problem with time_zone_offset

hm	14. oct. 2008	rev 1.4
	changed time_zone_offset from int to real to allow for half hour offset

hm	20. oct. 2006	rev 1.5
	changed time_zone_offset from Real to INT, now in Minutes

hm	27. feb. 2009	rev 1.6
	added type conversions to avoid warnings under codesys 3.0

ks	13. nov. 2009	rev 1.7
	corrected error in formula

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
