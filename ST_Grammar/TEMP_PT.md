(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SENSOR
*)
(*@KEY@:DESCRIPTION*)
version 1.7	11. mar. 2009
programmer 	hugo
tested by		oscat

this function returs the temperature for a platinum sensor for a range from -200..+850 °C

(*@KEY@:END_DESCRIPTION*)
FUNCTION TEMP_PT:REAL

(*Group:Default*)


VAR_INPUT
	RES :	REAL;
	R0 :	REAL;
END_VAR


VAR
	step :	REAL := REAL#50.0;
	X :	REAL;
	Y :	REAL;
	t1 :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: TEMP_PT
IEC_LANGUAGE: ST
*)
X := 3.9083E-3 * R0;
Y := -5.775E-7 * R0;
IF Res >= R0 THEN
	t1 := X * X - 4.0 * Y * (R0 - Res);
	IF t1 < 0.0 THEN
		TEMP_PT := 10000.0;
	ELSE
		TEMP_PT := (-X + SQRT(t1)) / (2.0 * Y);
	END_IF;
ELSE
	(* since the formula cannot be solved this is a successive approximation *)
	TEMP_PT := -100.0;
	WHILE step > 0.01 DO
		(* test if result greater or less *)
		IF RES_PT(TEMP_PT, R0) < res THEN TEMP_PT := TEMP_PT + step; ELSE TEMP_PT := TEMP_PT - step; END_IF;
		step := step * 0.5;
	END_WHILE;
END_IF;

(* revision history

rev 1.1 hm 24.1.2007	
	deleted unused variable C

rev 1.2 hm 10.9.2007
	reduced accuracy to 0.02 to shorten execution time

rev 1.3	hm	2. dec 2007
	changed code for better performance

rev	1.4	hm	23. dec 2007
	avoid a negative square root if input values are wrong

rev 1.5 hm	5. jan 2008
	replaced / 2 with * 0.5 for better performance

hm	31. oct. 2008	rev 1.6
	improved performance

hm	11. mar. 2009	rev 1.7
	changed real constants to use dot syntax

*)

(*@KEY@: END_WORKSHEET *)
END_FUNCTION
