Hospitals in Berlin

For datasets and statistics in Germany
https://www.destatis.de/EN/Home/_node.html
https://www-genesis.destatis.de/datenbank/online
https://daten.berlin.de/datensaetze

I got the data for Hospitals in Berlin from DKV website:

https://www.deutsches-krankenhaus-verzeichnis.de/app/suche/ergebnis

As per Berlin Health Excellence there are:
 More than 80 hospitals with about 20,000 beds
 More than 9,300 hospital physicians
 More than 9,200 outpatient resident physicians
 More than 13,000 enterprises of the healthcare industry
 More than 30 pharmacological enterprises

Process for data collection and cleaning
1. I copied the data form the DKV website and pasted it in the spreedsheet.
2. Through REGEXEXTRACT I extracted post code from the name.
3. By clicking on the hyperlink I got the address and location for the google maps.
4. Then I cleaned the Distance column by using Text to column fuction.
5. And removed the decimal from the rest numerical columns.
   
* Where ever the cases is 0 the hospital's data was not updated by the last quality report.

