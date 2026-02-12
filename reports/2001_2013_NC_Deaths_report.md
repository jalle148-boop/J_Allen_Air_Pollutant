Tabular Structure Report (Excel (2001_NC_Dealths))
============================================================

FILE METADATA
  Path      : C:\Users\schul\OneDrive - North Carolina Central University\Mentorship\Jasmine Allen\to_arcgis\2001_2013_NC_Deaths.xlsx
  Size      : 189.8 MB
  Extension : .xlsx

EXCEL SHEETS
  0: 2001_NC_Dealths  ← inspected
  1: 2002_NC_Dealths
  2: 2003_NC_Dealths
  3: 2004_NC_Dealths
  4: 2005_NC_Dealths
  5: 2006_NC_Dealths
  6: 2007_NC_Dealths
  7: 2008_NC_Dealths
  8: 2009_NC_Dealths
  9: 2010_NC_Dealths
  10: 2011_NC_Dealths
  11: 2012_NC_Dealths
  12: 2013_NC_Dealths

SHAPE
  Rows    : 72,844
  Columns : 29

COLUMN TYPES
  #    Column                              Pandas dtype       ArcGIS-compatible type
  ──────────────────────────────────────────────────────────────────────────────────
  0    INST                                int64              SHORT
  1    BEDCODE                             object             TEXT
  2    HOSPITAL                            object             TEXT
  3    EPLACE                              int64              LONG
  4    ECOUNTY                             int64              SHORT
  5    RPLACE                              int64              LONG
  6    RCOUNTY                             int64              SHORT
  7    DDATE                               datetime64[us]     DATE
  8    DMONTH                              int64              SHORT
  9    DDAY                                int64              SHORT
  10   DYEAR                               int64              SHORT
  11   SEX                                 int64              SHORT
  12   RACE                                int64              SHORT
  13   AGEYR                               float64            DOUBLE
  14   AGEMO                               int64              SHORT
  15   AGEDAY                              float64            DOUBLE
  16   CAUSE                               str                TEXT
  17   AUTOPSY                             int64              SHORT
  18   INJURY                              float64            DOUBLE
  19   BURIAL                              int64              SHORT
  20   MARITAL                             int64              SHORT
  21   ATTEND                              int64              SHORT
  22   RECORD                              int64              SHORT
  23   BSTATE                              int64              SHORT
  24   BCOUNTY                             int64              SHORT
  25   STATUS                              int64              SHORT
  26   ZIPCODE                             float64            DOUBLE
  27   HISPANIC                            str                TEXT
  28   EDUC                                int64              SHORT

MISSING VALUES
  BEDCODE                               35,272 missing  (48.4%)
  AGEYR                                      2 missing  (0.0%)
  AGEDAY                                     2 missing  (0.0%)
  INJURY                                68,546 missing  (94.1%)
  ZIPCODE                                   72 missing  (0.1%)

NUMERIC SUMMARY
  Column                                       Min          Max         Mean          Std
  ───────────────────────────────────────────────────────────────────────────────────────
  INST                                           0            9        2.514        3.048
  EPLACE                                       100        1e+05         6754    1.284e+04
  ECOUNTY                                        1          999        66.89        128.5
  RPLACE                                       100        1e+05         7797    1.613e+04
  RCOUNTY                                        1          999        77.56        161.3
  DMONTH                                         1           12        6.432        3.507
  DDAY                                           1           31        15.66        8.788
  DYEAR                                       2001         2001         2001            0
  SEX                                            1            2        1.506          0.5
  RACE                                           1            4        1.245       0.4727
  AGEYR                                          0           99        70.67        19.18
  AGEMO                                          0           99      0.01786       0.5948
  AGEDAY                                         0           27      0.03571       0.7604
  AUTOPSY                                        1            9        3.294         2.81
  INJURY                                         0            9        5.721         4.08
  BURIAL                                         1            9        1.594        1.249
  MARITAL                                        1            9         2.48       0.8729
  ATTEND                                         1            9        1.136       0.3705
  RECORD                                         2            2            2            0
  BSTATE                                         1           99        34.16        8.872
  BCOUNTY                                        1          999        358.6          444
  STATUS                                         1            8        4.012        2.953
  ZIPCODE                                      820     9.98e+04    2.806e+04         2379
  EDUC                                           0           99        12.88        14.31

TEXT / CATEGORICAL SUMMARY
  BEDCODE
    Unique values : 22
    Max length    : 1
    Sample values : ['P', 'B', 'I', 'N', 'F']
  HOSPITAL
    Unique values : 1,027
    Max length    : 7
    Sample values : ['7 00190', '0 00190', '1P00190', '0 00100', '7 00170']
  CAUSE
    Unique values : 1,594
    Max length    : 4
    Sample values : ['E149', 'C509', 'N390', 'J449', 'K703']
  HISPANIC
    Unique values : 7
    Max length    : 1
    Sample values : ['N', 'M', 'C', 'P', 'S']

DATE SUMMARY
  DDATE
    Min  : 2001-01-01 00:00:00
    Max  : 2001-12-31 00:00:00
    Span : 364 days 00:00:00

DUPLICATE ROWS
  21 fully duplicated row(s) detected.

COORDINATE / SPATIAL COLUMNS (ArcGIS XY detection)
  No obvious lat/lon columns found by name.
  Tip: ArcGIS Pro's 'XY Table to Point' tool expects columns
       named Latitude/Longitude (or X/Y) with numeric values.

SAMPLE ROWS (first 5)
   INST BEDCODE HOSPITAL  EPLACE  ECOUNTY  RPLACE  RCOUNTY      DDATE  DMONTH  DDAY  DYEAR  SEX  RACE  AGEYR  AGEMO  AGEDAY CAUSE  AUTOPSY  INJURY  BURIAL  MARITAL  ATTEND  RECORD  BSTATE  BCOUNTY  STATUS  ZIPCODE HISPANIC  EDUC
      7     NaN  7 00190     190        1     160        1 2001-01-01       1     1   2001    2     1   88.0      0     0.0  E149        9     NaN       1        3       1       2      34        1       8  27244.0        N     5
      0     NaN  0 00190     190        1     190        1 2001-01-01       1     1   2001    2     1   55.0      0     0.0  C509        9     NaN       1        2       1       2      34       68       6  27215.0        N    12
      1       P  1P00190     190        1    7900       79 2001-01-01       1     1   2001    2     1   91.0      0     0.0  N390        2     NaN       1        3       1       2      34       79       2  27320.0        N     6
      0     NaN  0 00100     100        1     100        1 2001-01-01       1     1   2001    2     2   65.0      0     0.0  C509        2     NaN       1        2       1       2      34        1       6  27349.0        N    11
      7     NaN  7 00170     170        1     170        1 2001-01-02       1     2   2001    2     1   79.0      0     0.0  J449        2     NaN       1        4       1       2      34        1       8  27253.0        N     8

ARCGIS PRO 3.5 IMPORT NOTES
  Import method: Map tab → Add Data → XY Table to Point (if spatial)
                 or Add Data → Table (for non-spatial attribute join)

  Encoding: Ensure CSV is saved as UTF-8 (ArcGIS Pro default).
  Date columns detected: ['DDATE']
  Tip: ArcGIS Pro parses ISO-8601 dates (YYYY-MM-DD) most reliably.
