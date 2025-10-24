This dataset presents the monthly commercial air traffic of French aerodromes since 1990. Monthly results are detailed for aerodromes that have achieved traffic equal to or greater than one traffic unit (UDT). The figures for aerodromes below this threshold are grouped into two separate rows according to their location : Metropolitan France (MT) or Overseas Territories (OM).

These are the columns of the dataset : 
- annee_mois (int64) : Year and month in YYYYMM format.
- code_aeroport (object) : Unique airport code.
- nom_aeroport (object) : Full name of the airport.
- zone (object) : Geographical zone of the airport.
- unites_trafic (int64) : Traffic unit.
- passagers_depart (int64) : Number of departing passengers.
- passagers_arrivee (int64) : Number of arriving passengers.
- passagers_transit (int64) : Number of transit passengers.
- fret_depart (float64) : Amount of cargo (in tonnes) departing.
- fret_arrivee (float64) : Amount of cargo (in tonnes) arriving.
- mouvements_passagers (int64) : Number of aircraft movements carrying passengers.
- mouvements_cargo (int64) : Number of aircraft movements carrying cargo.
- source (object) : Name of the file source.
- annee (int64) : Year extracted from "annee_mois".
- mois (int64) : Month extracted from "annee_mois" (1 to 12).

