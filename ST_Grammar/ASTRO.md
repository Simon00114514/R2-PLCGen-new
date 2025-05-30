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
FUNCTION_BLOCK ASTRO

(*Group:Default*)


VAR_INPUT
	M :	REAL;
	AE :	REAL;
	PC :	REAL;
	LJ :	REAL;
END_VAR


VAR_OUTPUT
	YM :	REAL;
	YAE :	REAL;
	YPC :	REAL;
	YLJ :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: ASTRO
IEC_LANGUAGE: ST
*)
YAE :=	AE
		+ m * 6.6845871535E-012
		+ PC * 206265.0
		+ LJ * 63240.0;
Ym := YAE * 149.597870E9;
YPC := YAE * 4.8481322570E-006;
YLJ := YAE * 1.5812776724E-005;


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
