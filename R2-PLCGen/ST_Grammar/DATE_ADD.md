(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: TIME_DATE
*)
(*@KEY@:DESCRIPTION*)
version 1.8		22. mar. 2011
programmer 	    hugo
tested by		oscat

date_add adds days, weeks, month or years to a date.
negative inputs are allowed for subtraction.

(*@KEY@:END_DESCRIPTION*)
FUNCTION DATE_ADD:UDINT

(*Group:Default*)


VAR_INPUT
	IDATE :	UDINT;
	D :	INT;
	W :	INT;
	M :	INT;
	Y :	INT;
END_VAR


VAR
	mo :	INT;
	yr :	INT;
	dm :	INT;
END_VAR


(*@KEY@: WORKSHEET
NAME: DATE_ADD
IEC_LANGUAGE: ST
*)
DATE_ADD := IDATE + INT_TO_UDINT(D + W * 7) * UDINT#86400;
yr := Y + YEAR_OF_DATE(DATE_ADD);
mo := M + MONTH_OF_DATE(DATE_ADD);
dm := DAY_OF_MONTH(DATE_ADD);
WHILE mo > 12 DO
	mo := mo - 12;
	yr := yr + 1;
END_WHILE;
WHILE mo < 1 DO
	mo := mo + 12;
	yr := yr - 1;
END_WHILE;
DATE_ADD := SET_DATE(yr, mo, dm);

(* revision history

hm 27.12.2006	rev 1.0
	nrw module

hm 12.4.2007		rev 1.1
	corrected an error while date would be incorrect when year  = 0

hm	1.11.2007		rev 1.2
	added int_to_dword stetements to avoid possible overrun with möller ecp4

hm	22. mar. 2008	rev 1.3
	fixed some bugs when month was negative

hm	7. oct. 2008	rev 1.4
	changed function year to year_of_date
	changed function month to month_of_date

hm	29. mar. 2009	rev 1.5
	improved performance

hm	27. jan. 2011	rev 1.6
	faster code

hm	2. feb. 2011		rev 1.7
	fixed an error, weeks not calculated

hm	22. mar. 2011	rev 1.8
	fixed an error in formula
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
