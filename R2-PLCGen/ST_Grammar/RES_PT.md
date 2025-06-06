(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SENSOR
*)
(*@KEY@:DESCRIPTION*)
version 1.3	11. mar. 2009
programmer 	hugo
tested by	oscat


this function returs the resistance for a platinum sensor for a temperature range from -200..+850 °C

(*@KEY@:END_DESCRIPTION*)
FUNCTION RES_PT:REAL

(*Group:Default*)


VAR_INPUT
	T :	REAL;
	R0 :	REAL;
END_VAR


VAR
	T2 :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: RES_PT
IEC_LANGUAGE: ST
*)
T2 := T * T;

IF T >= 0.0 THEN
	RES_PT := R0 * ( 1.0 + 3.90802E-3 * T + -5.802E-7 * T2);
ELSE
	RES_PT := R0 * ( 1.0 + 3.90802E-3 * T + -5.802E-7 * T2 + -4.27350E-12 * (T - 100.0) * T2 * T);
END_IF;



(* revision history
hm	4. aug. 2006	rev 1.1
	original version

hm	2. dec 2007	rev 1.2
	changed code for better performance

hm	11. mar. 2009	rev 1.3
	changed real constants to use dot syntax

*)


(*
 Auszug aus DIN 43760 für Pt100

°C		R		°C		R		°C	R			°C		R			°C		R			°C		R

-200 	18,49 	-100 	60,25 	0 	100,00 	100 	138,50 	200 	175,84 	300 	212,02
-195 	20,65 	-95 	62,28 	5 	101,95 	105 	140,39 	205 	177,68 	305 	213,80
-190 	22,80 	-90 	64,30 	10 	103,90 	110 	142,29 	210 	179,51 	310 	215,57
-185 	24,94 	-85 	66,31 	15 	105,85 	115 	144,17 	215 	181,34 	315 	217,35
-180 	27,08 	-80 	68,33 	20 	107,79 	120 	146,06 	220 	183,17 	320 	219,12
-175 	29,20 	-75 	70,33 	25 	109,73 	125 	147,94 	225 	184,99 	325 	220,88
-170 	31,32 	-70 	72,33 	30 	111,67 	130 	149,82 	230 	186,82 	330 	222,65
-165 	33,43 	-65 	74,33 	35 	113,61 	135 	151,70 	235 	188,63 	335 	224,41
-160 	35,33 	-60 	76,33 	40 	115,54 	140 	153,58 	240 	190,45 	340 	226,17
-155 	37,63 	-55 	78,32 	45 	117,47 	145 	155,45 	245 	192,26 	345 	227,92
-150 	39,71 	-50 	80,31 	50 	119,40 	150 	157,31 	250 	194,07 	350 	229,67
-145 	41,79 	-45 	82,29 	55 	121,32 	155 	159,18 	255 	195,88 	355 	231,42
-140 	43,87 	-40 	84,27 	60 	123,24 	160 	161,04 	260 	197,69 	360 	233,17
-135 	45,94 	-35 	86,25 	65 	125,16 	165 	162,90 	265 	199,49 	365 	234,91
-130 	48,00 	-30 	88,22 	70 	127,07 	170 	164,76 	270 	201,29 	370 	236,65
-125 	50,06 	-25 	90,19 	75 	128,98 	175 	166,61 	275 	203,08 	375 	238,39
-120 	52,11 	-20 	92,16 	80 	130,89 	180 	168,46 	280 	204,88 	380 	240,13
-115 	54,15 	-15 	94,12 	85 	132,80 	185 	170,31 	285 	206,67 	385 	241,86
-110 	56,19 	-10 	96,09 	90 	134,70 	190 	172,16 	290 	208,45 	390 	243,59
-105 	58,22 	-5 		98,04 	95 	136,60 	195 	174,00 	295 	210,24 	395 	245,31

*)
(*
revision history


*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
