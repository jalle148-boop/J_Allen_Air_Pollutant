Tabular Structure Report (Excel (2014_NC_Deaths))
============================================================

FILE METADATA
  Path      : C:\Users\schul\OneDrive - North Carolina Central University\Mentorship\Jasmine Allen\to_arcgis\2014_2021_NC_Deaths.xlsx
  Size      : 144.0 MB
  Extension : .xlsx

EXCEL SHEETS
  0: 2014_NC_Deaths  ← inspected
  1: 2015_NC_Deaths
  2: 2016_NC_Deaths
  3: 2017_NC_Deaths
  4: 2018_NC_Deaths
  5: 2019_NC_Deaths
  6: 2020_NC_Deaths
  7: 2021_NC_Deaths

SHAPE
  Rows    : 88,000
  Columns : 56

COLUMN TYPES
  #    Column                              Pandas dtype       ArcGIS-compatible type
  ──────────────────────────────────────────────────────────────────────────────────
  0    DPLACE                              int64              SHORT
  1    CNTYOCC                             int64              SHORT
  2    CITYOCC                             int64              LONG
  3    DSTATE                              str                TEXT
  4    COUNTYC                             int64              SHORT
  5    CITYC                               int64              LONG
  6    STATEC                              str                TEXT
  7    B_CNT                               str                TEXT
  8    B_ST                                str                TEXT
  9    B_CORES                             int64              SHORT
  10   DHTDATE                             datetime64[us]     DATE
  11   DHTMO                               int64              SHORT
  12   DHTDAY                              int64              SHORT
  13   DHTYR                               int64              SHORT
  14   SEX                                 str                TEXT
  15   RACER                               int64              SHORT
  16   HISP                                str                TEXT
  17   AGEYRS                              int64              SHORT
  18   AGEMTHS                             float64            DOUBLE
  19   AGEDAYS                             float64            DOUBLE
  20   MARITAL                             str                TEXT
  21   DEDUC                               int64              SHORT
  22   CERTCODE                            int64              SHORT
  23   MECASE                              str                TEXT
  24   MEDECL                              str                TEXT
  25   PLACE                               float64            DOUBLE
  26   DISP                                str                TEXT
  27   VETERAN                             str                TEXT
  28   ACMECOD                             str                TEXT
  29   FILLER                              float64            DOUBLE
  30   COD1                                str                TEXT
  31   COD2                                str                TEXT
  32   COD3                                str                TEXT
  33   COD4                                str                TEXT
  34   COD5                                str                TEXT
  35   COD6                                str                TEXT
  36   COD7                                str                TEXT
  37   COD8                                str                TEXT
  38   COD9                                str                TEXT
  39   COD10                               str                TEXT
  40   COD11                               str                TEXT
  41   COD12                               str                TEXT
  42   COD13                               str                TEXT
  43   COD14                               str                TEXT
  44   COD15                               str                TEXT
  45   COD16                               str                TEXT
  46   COD17                               str                TEXT
  47   COD18                               str                TEXT
  48   COD19                               str                TEXT
  49   COD20                               str                TEXT
  50   AUTOPSY                             str                TEXT
  51   FINDINGS                            str                TEXT
  52   TOBACCO                             str                TEXT
  53   PREG                                float64            DOUBLE
  54   WORKINJ                             str                TEXT
  55   ZIPCODE                             float64            DOUBLE

MISSING VALUES
  DHTDATE                                    1 missing  (0.0%)
  AGEMTHS                               87,096 missing  (99.0%)
  AGEDAYS                               87,375 missing  (99.3%)
  PLACE                                 82,080 missing  (93.3%)
  FILLER                                88,000 missing  (100.0%)
  PREG                                      24 missing  (0.0%)
  ZIPCODE                                  660 missing  (0.8%)

NUMERIC SUMMARY
  Column                                       Min          Max         Mean          Std
  ───────────────────────────────────────────────────────────────────────────────────────
  DPLACE                                         1            9        3.643        2.026
  CNTYOCC                                        1          888        114.9        121.6
  CITYOCC                                        0        1e+05    2.748e+04    2.642e+04
  COUNTYC                                        1          888        124.9        148.4
  CITYC                                          0        1e+05    2.235e+04     2.69e+04
  B_CORES                                        1          999        417.8        390.2
  DHTMO                                          1           12        6.506        3.528
  DHTDAY                                         1           99         15.7        8.818
  DHTYR                                       2014         2014         2014            0
  RACER                                          1            4         1.27        0.557
  AGEYRS                                         0          113        71.91         18.3
  AGEMTHS                                        0           11        1.235        2.506
  AGEDAYS                                        0           27        2.856        6.135
  DEDUC                                          1            9        3.359        1.737
  CERTCODE                                       1            9        1.493        1.244
  PLACE                                          0            9        4.257        4.237
  FILLER                                       nan          nan          nan          nan
  PREG                                           1            9        4.761        3.521
  ZIPCODE                                      687    9.951e+04    2.808e+04         2635

TEXT / CATEGORICAL SUMMARY
  DSTATE
    Unique values : 47
    Max length    : 2
    Sample values : ['NC', 'CO', 'DE', 'HI', 'MS']
  STATEC
    Unique values : 55
    Max length    : 2
    Sample values : ['NC', 'IN', 'SC', 'TN', 'NY']
  B_CNT
    Unique values : 137
    Max length    : 2
    Sample values : ['US', 'GM', 'ZZ', 'CU', 'KN']
  B_ST
    Unique values : 57
    Max length    : 2
    Sample values : ['NY', 'NC', 'MD', 'TN', 'WI']
  SEX
    Unique values : 3
    Max length    : 1
    Sample values : ['F', 'M', 'U']
  HISP
    Unique values : 7
    Max length    : 1
    Sample values : ['N', 'C', 'P', 'S', 'U']
  MARITAL
    Unique values : 6
    Max length    : 1
    Sample values : ['W', 'D', 'M', 'S', 'U']
  MECASE
    Unique values : 3
    Max length    : 1
    Sample values : ['N', 'Y', 'U']
  MEDECL
    Unique values : 4
    Max length    : 1
    Sample values : ['N', 'Y', ' ', 'U']
  DISP
    Unique values : 7
    Max length    : 1
    Sample values : ['B', 'C', 'E', 'R', 'D']
  VETERAN
    Unique values : 3
    Max length    : 1
    Sample values : ['N', 'Y', 'U']
  ACMECOD
    Unique values : 1,644
    Max length    : 4
    Sample values : ['E870', 'C679', 'E86', 'C349', 'G309']
  COD1
    Unique values : 1,644
    Max length    : 4
    Sample values : ['E870', 'C679', 'E86', 'C349', 'G309']
  COD2
    Unique values : 1,294
    Max length    : 4
    Sample values : ['E039', 'D649', 'I10', 'I500', 'J449']
  COD3
    Unique values : 1,238
    Max length    : 4
    Sample values : ['E785', 'N19', 'I739', 'J690', ' ']
  COD4
    Unique values : 1,037
    Max length    : 4
    Sample values : ['G309', ' ', 'R628', 'J969', 'R99']
  COD5
    Unique values : 785
    Max length    : 4
    Sample values : ['I48', ' ', 'I255', 'E785', 'I500']
  COD6
    Unique values : 595
    Max length    : 4
    Sample values : [' ', 'N185', 'I10', 'J449', 'J189']
  COD7
    Unique values : 435
    Max length    : 4
    Sample values : [' ', 'R092', 'I469', 'R628', 'I500']
  COD8
    Unique values : 269
    Max length    : 4
    Sample values : [' ', 'J189', 'M109', 'W80', 'I461']
  COD9
    Unique values : 166
    Max length    : 4
    Sample values : [' ', 'J90', 'M625', 'R688', 'R522']
  COD10
    Unique values : 96
    Max length    : 4
    Sample values : [' ', 'T910', 'K567', 'J960', 'L022']
  COD11
    Unique values : 46
    Max length    : 4
    Sample values : [' ', 'T940', 'R601', 'J961', 'J960']
  COD12
    Unique values : 18
    Max length    : 4
    Sample values : [' ', 'T941', 'R91', 'J969', 'R628']
  COD13
    Unique values : 7
    Max length    : 4
    Sample values : [' ', 'T814', 'N390', 'W80', 'N179']
  COD14
    Unique values : 3
    Max length    : 4
    Sample values : [' ', 'R628', 'X590']
  COD15
    Unique values : 1
    Max length    : 1
    Sample values : [' ']
  COD16
    Unique values : 1
    Max length    : 1
    Sample values : [' ']
  COD17
    Unique values : 1
    Max length    : 1
    Sample values : [' ']
  COD18
    Unique values : 1
    Max length    : 1
    Sample values : [' ']
  COD19
    Unique values : 1
    Max length    : 1
    Sample values : [' ']
  COD20
    Unique values : 1
    Max length    : 1
    Sample values : [' ']
  AUTOPSY
    Unique values : 4
    Max length    : 1
    Sample values : ['N', ' ', 'Y', 'U']
  FINDINGS
    Unique values : 5
    Max length    : 1
    Sample values : ['N', ' ', 'Y', 'U', 'X']
  TOBACCO
    Unique values : 6
    Max length    : 1
    Sample values : ['N', 'U', 'P', 'Y', 'C']
  WORKINJ
    Unique values : 5
    Max length    : 1
    Sample values : [' ', 'N', 'Y', 'U', 'X']

DATE SUMMARY
  DHTDATE
    Min  : 2014-01-01 00:00:00
    Max  : 2014-12-31 00:00:00
    Span : 364 days 00:00:00

DUPLICATE ROWS
  17 fully duplicated row(s) detected.

COORDINATE / SPATIAL COLUMNS (ArcGIS XY detection)
  No obvious lat/lon columns found by name.
  Tip: ArcGIS Pro's 'XY Table to Point' tool expects columns
       named Latitude/Longitude (or X/Y) with numeric values.

SAMPLE ROWS (first 5)
   DPLACE  CNTYOCC  CITYOCC DSTATE  COUNTYC  CITYC STATEC B_CNT B_ST  B_CORES    DHTDATE  DHTMO  DHTDAY  DHTYR SEX  RACER HISP  AGEYRS  AGEMTHS  AGEDAYS MARITAL  DEDUC  CERTCODE MECASE MEDECL  PLACE DISP VETERAN ACMECOD  FILLER COD1 COD2 COD3 COD4 COD5 COD6 COD7 COD8 COD9 COD10 COD11 COD12 COD13 COD14 COD15 COD16 COD17 COD18 COD19 COD20 AUTOPSY FINDINGS TOBACCO  PREG WORKINJ  ZIPCODE
        4        1    27280     NC        1  27280     NC    US   NY      888 2014-01-01      1       1   2014   F      1    N      83      NaN      NaN       W      2         1      N      N    NaN    B       N    E870     NaN E870 E039 E785 G309  I48                                                                                             N        N       N   1.0          27253.0
        6        1    27280     NC        1   9060     NC    US   NC        1 2014-01-01      1       1   2014   M      2    N      71      NaN      NaN       D      2         1      N      N    NaN    B       N    C679     NaN C679 D649  N19                                                                                                       N        N       U   8.0          27217.0
        4        1    27280     NC        1      0     NC    US   NC        1 2014-01-01      1       1   2014   F      1    N      83      NaN      NaN       W      1         1      N      N    NaN    B       N    C679     NaN C679  I10 I739                                                                                                       N                N   1.0          27253.0
        1        1     9060     NC        1      0     NC    US   MD      888 2014-01-01      1       1   2014   F      2    N      96      NaN      NaN       W      1         1      N      N    NaN    B       N     E86     NaN  E86 I500 J690                                                                                                       N        N       N   1.0          27244.0
        5        1     9060     NC        1  27280     NC    US   NC      127 2014-01-01      1       1   2014   M      1    N      63      NaN      NaN       M      3         4      N      N    NaN    B       N    C349     NaN C349 J449                                                                                                            N        N       U   8.0          27253.0

ARCGIS PRO 3.5 IMPORT NOTES
  Import method: Map tab → Add Data → XY Table to Point (if spatial)
                 or Add Data → Table (for non-spatial attribute join)

  Encoding: Ensure CSV is saved as UTF-8 (ArcGIS Pro default).
  Date columns detected: ['DHTDATE']
  Tip: ArcGIS Pro parses ISO-8601 dates (YYYY-MM-DD) most reliably.
