(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: TIME_DATE
*)
(*@KEY@:DESCRIPTION*)
version 2.0	18. jans 2011
programmer 	hugo
tested by	tobias

holiday calculates if a given day is a holiday and displays the name of the holiday as string as well as a boolean flag to indicate a holiday.
the holidays are specified in the country setup under global constants.
a holiday can be of fixed date for example new years day on january 1st.
a holiday can have a fixed offset from easter sunday as for most church holidays.
a holiday can be a specific weekday before a fixed date, for example buss und bettag is the last wednesday before nov 23rd.
with a simple f_use flag any specific holiday can be turned on or off if needed.

please check the manual for examples of holiday definitions

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK HOLIDAY

(*Group:Parameter*)


VAR_INPUT
	DATE_IN :	UDINT;
	LANGU :	INT;
	FRIDAY :	BOOL;
	SATURDAY :	BOOL;
	SUNDAY :	BOOL;
END_VAR


VAR_OUTPUT
	Y :	BOOL;
	NAME :	oscat_STRING30;
END_VAR


VAR_IN_OUT
	HOLIDAYS :	oscat_HOLIDAY_DATA_0_29;
END_VAR


(*Group:lokal*)


VAR
	size :	INT := INT#29;
	last_active :	UDINT;
	ostern :	UDINT;
	i :	INT;
	jahr :	INT;
	x_date :	UDINT;
	lx :	INT;
	wdx :	INT;
	SETUP_LOCATION :	SETUP_LOCATION;
	SETUP_WEEKDAYS :	SETUP_WEEKDAYS;
	SETUP_LANGUAGE :	SETUP_LANGUAGE;
	LOCATION :	oscat_LOCATION;
	WEEKDAYS :	oscat_WEEKDAYS;
	LANGUAGE :	oscat_LANGUAGE;
	wd :	INT;
END_VAR


(*@KEY@: WORKSHEET
NAME: HOLIDAY
IEC_LANGUAGE: ST
*)
(* for performance reasons only activate once a day *)
IF last_active = date_in THEN RETURN; END_IF;
last_active := DATE_IN;

SETUP_LOCATION(LOCATION:=LOCATION);
LOCATION:=SETUP_LOCATION.LOCATION;

SETUP_WEEKDAYS(WEEKDAYS:=WEEKDAYS);
WEEKDAYS:=SETUP_WEEKDAYS.WEEKDAYS;

SETUP_LANGUAGE(LANGUAGE:=LANGUAGE);
LANGUAGE:=SETUP_LANGUAGE.LANGUAGE;

(* determine language *)
IF LANGU = 0 THEN
	lx := language.DEFAULT;
ELSE
	lx := MIN(language.LMAX, LANGU);
END_IF;

(* berechnung von ostern für das aktuelle jahr *)
jahr := YEAR_OF_DATE(date_in);
ostern := EASTER(jahr);
wdx := DAY_OF_WEEK(DATE_IN);
Y := FALSE;

(* check for holidays *)
FOR i := 0 TO size DO
	x_date := SET_DATE(jahr, SINT_TO_INT(HOLIDAYS[i].MONTH) , SINT_TO_INT(HOLIDAYS[i].DAY));
	IF HOLIDAYS[i].USE = SINT#1 AND HOLIDAYS[i].MONTH > SINT#0 THEN
		(* check for fixed date holiday *)
		IF x_date = date_in THEN
			Y := TRUE;
			NAME := HOLIDAYS[i].NAME;
			RETURN;
		END_IF;
	ELSIF HOLIDAYS[i].USE = SINT#1 AND HOLIDAYS[i].MONTH = SINT#0 THEN
		(* check for holiday in reference to easter *)
		IF DATE_ADD(ostern, SINT_TO_INT(HOLIDAYS[i].DAY),0,0,0) = date_in THEN
			Y := TRUE;
			NAME := HOLIDAYS[i].NAME;
			RETURN;
		END_IF;
	ELSIF HOLIDAYS[i].USE < SINT#0 THEN
		(* check for holiday on a weekday before date *)
		IF DAY_OF_WEEK(date_in) = SINT_TO_INT(ABS(HOLIDAYS[i].USE)) AND date_in < x_date AND date_in >= DATE_ADD(x_date,-7,0,0,0) THEN
			Y := TRUE;
			NAME := HOLIDAYS[i].NAME;
			RETURN;
		END_IF;
	END_IF;
END_FOR;

(* check array if today is weekend *)
IF NOT Y AND (wdx = 5 AND FRIDAY OR wdx = 6 AND SATURDAY OR wdx = 7 AND SUNDAY) THEN
	Y := TRUE;
	wd := LOCATION.LANGUAGE[lx];
	NAME := WEEKDAYS[wd][wdx];
ELSE
	NAME := '';
END_IF;


(*
Neujahrstag 	1. Januar 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
Heilige Drei Könige 	6. Januar 	• 	• 												• 		
Karfreitag 	Ostersonntag - 2d 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
Ostersonntag 	siehe Osterdatum 				(•) 												
Ostermontag 	Ostersonntag + 1d 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
Tag der Arbeit 	1. Mai 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
Christi Himmelfahrt 	Ostersonntag + 39d 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
Pfingstsonntag 	Ostersonntag + 49d 				(•) 												
Pfingstmontag 	Ostersonntag + 50d 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
Fronleichnam 	Ostersonntag + 60d 	• 	• 					• 			• 	• 	• 	1) 			2)
Augsburger Friedensfest 	8. August 		(3) 														
Mariä Himmelfahrt 	15. August 		(5) 										• 				
Tag der Deutschen Einheit 	3. Oktober 6) 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
Reformationstag 	31. Oktober 				• 				• 					• 	• 		•
Allerheiligen 	1. November 	• 	• 								• 	• 	• 				
Buß- und Bettag 4) 	Mittwoch vor dem 23.11. 			7 										• 			
1. Weihnachtstag 	25. Dezember 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
2. Weihnachtstag 	26. Dezember 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	• 	•
*)



(* revision history
hm 	27. feb. 2007	rev 1.1
	deleted unused variable init

hm	31. oct. 2007	rev 1.2
	changed holiday definition from constant to input constant to allow easier changes by user without recompilation of the lib

hm 	24. nov. 2007	rev 1.3
	changes F_use of  Buß_und_Bettag to 0 because this is no official holiday

hm	7. apr. 2008	rev 1.4
	improved performance

hm	7. oct. 2008	rev 1.5
	changed code to use setup data from global constants
	changed length of output NAME from 20 to 30
	holiday will now also be indicated on a weekend
	changed function year to year_of_date
	changed function weekday to day_of_week

hm	21. oct. 2008	rev 1.6
	using location constants

hm	18. jan 2011	rev 2.0
	using user specified array for holidays

*)


(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
