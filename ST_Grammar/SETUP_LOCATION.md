(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: SETUP
*)
(*@KEY@:DESCRIPTION*)

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK SETUP_LOCATION

(*Group:Default*)


VAR_IN_OUT
	LOCATION :	oscat_LOCATION;
END_VAR


VAR
	init :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: SETUP_LOCATION
IEC_LANGUAGE: ST
*)
(* Daten initialisieren *)
IF init THEN RETURN; END_IF;
init := TRUE;

LOCATION.DEFAULT  := 1;  (* 1=germany, 2=austria 3=france 4=belgium-german 5= italien-Südtirol *)
LOCATION.LMAX := 5;

LOCATION.LANGUAGE[1] := 2;
LOCATION.LANGUAGE[2] := 2;
LOCATION.LANGUAGE[3] := 3;
LOCATION.LANGUAGE[4] := 2;
LOCATION.LANGUAGE[5] := 2;

(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
