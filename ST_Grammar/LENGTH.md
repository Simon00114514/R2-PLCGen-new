(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.CONVERSION
*)
(*@KEY@:DESCRIPTION*)
version 1.1	11. mar. 2009
programmer 	hugo
tested by	oscat

this function converts different length units
any unused input can simply be left open.
different inputs connected at the same time will be added up.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK LENGTH

(*Group:Default*)


VAR_INPUT
	M :	REAL;
	P :	REAL;
	IN :	REAL;
	FT :	REAL;
	YD :	REAL;
	MILE :	REAL;
	SM :	REAL;
	FM :	REAL;
END_VAR


VAR_OUTPUT
	YM :	REAL;
	YP :	REAL;
	YIN :	REAL;
	YFT :	REAL;
	YYD :	REAL;
	YMILE :	REAL;
	YSM :	REAL;
	YFM :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: LENGTH
IEC_LANGUAGE: ST
*)
Ym :=	m
		+ p * 0.000376065
		+ in * 0.0254
		+ ft * 0.3048
		+ yd * 0.9144
		+ mile * 1609.344
		+ sm * 1852.0
		+ fm * 1.829;
Yp := Ym * 2659.11478068951;
Yin := Ym * 39.37007874016;
Yft := Ym * 3.28083989501;
Yyd := Ym * 1.09361329834;
Ymile := Ym * 0.00062137119;
Ysm := Ym * 0.00053995680;
Yfm := Ym * 0.54674685621;

(*
Länge Meter m SI-Basiseinheit
Astronomische Einheit* AE 1 AE = 149,597 870 · E9 m
Parsec pc 1 pc = 206265 AE = 30,857 · E15 m
Lichtjahr Lj 1 Lj = 9,460 530 · E15 m = 63240 AE = 0,306 59 pc
Ångström Å 1 Å = E–l0 m
typograph. Punkt p 1 p = 0,376 065 mm • im Druckereigewerbe
inch** in 1 in = 2,54 · E–2 m = 25,4 mm***
foot ft 1 ft = 0,3048 m = 30,48 cm
yard yd 1 yd = 0,9144 m
mile mile 1 mile = 1609,344 m
Internat. Seemeile sm 1 sm = 1852 m
Fathom fm 1 fm = 1,829 m • in der Seeschifffahrt
*)

(* revision history

hm	27. mar. 2007	rev 1.0
	original version

hm	11. mar. 2009	rev 1.1
	improved code

*)

(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
