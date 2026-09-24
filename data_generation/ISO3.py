"""Run this via `make climate_categories/data/ISO3.yaml` in the main directory."""

import datetime
import itertools
import pathlib

import requests
from utils import write_categorization

import climate_categories

URL = (
    "https://salsa.debian.org/iso-codes-team/iso-codes/-/raw/main/data/"
    "iso_3166-1.json?inline=false"
)
OUTPATH = pathlib.Path("./climate_categories/data/ISO3.yaml")
LAST_UPDATE = datetime.date(2026, 9, 24)

# Status of the UNFCCC at its depositary, the Secretary-General of the United Nations.
# Lists the date on which every party deposited its instrument of ratification,
# acceptance, approval, accession, or succession.
UNTC_UNFCCC_STATUS = (
    "https://treaties.un.org/Pages/ViewDetailsIII.aspx?src=TREATY&mtdsg_no=XXVII-7"
    "&chapter=27&Temp=mtdsg3&clang=_en"
)

# Parties to the UNFCCC with the date on which the Convention entered into force for
# them and a reference for it, in the order in which they joined. According to
# article 23 of the Convention (https://unfccc.int/resource/docs/convkp/conveng.pdf),
# the Convention entered into force on 1994-03-21 for all parties which deposited
# their instrument until 1993-12-21, and enters into force 90 days after the deposit
# for all later parties. For parties which joined until 2000, we give the depositary's
# status page as reference, for later parties the depositary notification. The
# Federal Republic of Yugoslavia acceded in 2001, the depositary lists this as the
# accession of Serbia. Montenegro became a party by succession, effective from its
# independence.
UNFCCC_JOINED: list[tuple[str, datetime.date, str]] = [
    ("ARM", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ATG", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("AUS", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("BFA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CAN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CHE", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CHN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("COK", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CZE", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("DEU", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("DMA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("DNK", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("DZA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ECU", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ESP", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("EU", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("FJI", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("FSM", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("GBR", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("GIN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("IND", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ISL", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("JOR", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("JPN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("KNA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("KOR", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("LCA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("LKA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MCO", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MDV", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MEX", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MHL", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MNG", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MUS", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("NLD", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("NOR", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("NRU", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("NZL", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("PER", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("PNG", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("PRT", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("SDN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("SWE", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("SYC", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("TUN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("TUV", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("UGA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("USA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("UZB", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("VUT", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ZMB", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ZWE", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CUB", datetime.date(1994, 4, 5), UNTC_UNFCCC_STATUS),
    ("MRT", datetime.date(1994, 4, 20), UNTC_UNFCCC_STATUS),
    ("BWA", datetime.date(1994, 4, 27), UNTC_UNFCCC_STATUS),
    ("HUN", datetime.date(1994, 5, 25), UNTC_UNFCCC_STATUS),
    ("PRY", datetime.date(1994, 5, 25), UNTC_UNFCCC_STATUS),
    ("AUT", datetime.date(1994, 5, 29), UNTC_UNFCCC_STATUS),
    ("BRA", datetime.date(1994, 5, 29), UNTC_UNFCCC_STATUS),
    ("ARG", datetime.date(1994, 6, 9), UNTC_UNFCCC_STATUS),
    ("MLT", datetime.date(1994, 6, 15), UNTC_UNFCCC_STATUS),
    ("BRB", datetime.date(1994, 6, 21), UNTC_UNFCCC_STATUS),
    ("FRA", datetime.date(1994, 6, 23), UNTC_UNFCCC_STATUS),
    ("BHS", datetime.date(1994, 6, 27), UNTC_UNFCCC_STATUS),
    ("ETH", datetime.date(1994, 7, 4), UNTC_UNFCCC_STATUS),
    ("BGD", datetime.date(1994, 7, 14), UNTC_UNFCCC_STATUS),
    ("ITA", datetime.date(1994, 7, 14), UNTC_UNFCCC_STATUS),
    ("IRL", datetime.date(1994, 7, 19), UNTC_UNFCCC_STATUS),
    ("MWI", datetime.date(1994, 7, 20), UNTC_UNFCCC_STATUS),
    ("NPL", datetime.date(1994, 7, 31), UNTC_UNFCCC_STATUS),
    ("FIN", datetime.date(1994, 8, 1), UNTC_UNFCCC_STATUS),
    ("LUX", datetime.date(1994, 8, 7), UNTC_UNFCCC_STATUS),
    ("PAK", datetime.date(1994, 8, 30), UNTC_UNFCCC_STATUS),
    ("TCD", datetime.date(1994, 9, 5), UNTC_UNFCCC_STATUS),
    ("ROU", datetime.date(1994, 9, 6), UNTC_UNFCCC_STATUS),
    ("GMB", datetime.date(1994, 9, 8), UNTC_UNFCCC_STATUS),
    ("LIE", datetime.date(1994, 9, 20), UNTC_UNFCCC_STATUS),
    ("TTO", datetime.date(1994, 9, 22), UNTC_UNFCCC_STATUS),
    ("BEN", datetime.date(1994, 9, 28), UNTC_UNFCCC_STATUS),
    ("MYS", datetime.date(1994, 10, 11), UNTC_UNFCCC_STATUS),
    ("EST", datetime.date(1994, 10, 25), UNTC_UNFCCC_STATUS),
    ("POL", datetime.date(1994, 10, 26), UNTC_UNFCCC_STATUS),
    ("GEO", datetime.date(1994, 10, 27), UNTC_UNFCCC_STATUS),
    ("PHL", datetime.date(1994, 10, 31), UNTC_UNFCCC_STATUS),
    ("GRC", datetime.date(1994, 11, 2), UNTC_UNFCCC_STATUS),
    ("GRD", datetime.date(1994, 11, 9), UNTC_UNFCCC_STATUS),
    ("URY", datetime.date(1994, 11, 16), UNTC_UNFCCC_STATUS),
    ("IDN", datetime.date(1994, 11, 21), UNTC_UNFCCC_STATUS),
    ("SVK", datetime.date(1994, 11, 23), UNTC_UNFCCC_STATUS),
    ("CRI", datetime.date(1994, 11, 24), UNTC_UNFCCC_STATUS),
    ("GUY", datetime.date(1994, 11, 27), UNTC_UNFCCC_STATUS),
    ("NGA", datetime.date(1994, 11, 27), UNTC_UNFCCC_STATUS),
    ("KEN", datetime.date(1994, 11, 28), UNTC_UNFCCC_STATUS),
    ("ALB", datetime.date(1995, 1, 1), UNTC_UNFCCC_STATUS),
    ("BOL", datetime.date(1995, 1, 1), UNTC_UNFCCC_STATUS),
    ("SEN", datetime.date(1995, 1, 15), UNTC_UNFCCC_STATUS),
    ("CMR", datetime.date(1995, 1, 17), UNTC_UNFCCC_STATUS),
    ("SMR", datetime.date(1995, 1, 26), UNTC_UNFCCC_STATUS),
    ("BLZ", datetime.date(1995, 1, 29), UNTC_UNFCCC_STATUS),
    ("COM", datetime.date(1995, 1, 29), UNTC_UNFCCC_STATUS),
    ("VNM", datetime.date(1995, 2, 14), UNTC_UNFCCC_STATUS),
    ("MMR", datetime.date(1995, 2, 23), UNTC_UNFCCC_STATUS),
    ("CIV", datetime.date(1995, 2, 27), UNTC_UNFCCC_STATUS),
    ("WSM", datetime.date(1995, 2, 27), UNTC_UNFCCC_STATUS),
    ("EGY", datetime.date(1995, 3, 5), UNTC_UNFCCC_STATUS),
    ("PRK", datetime.date(1995, 3, 5), UNTC_UNFCCC_STATUS),
    ("LBN", datetime.date(1995, 3, 15), UNTC_UNFCCC_STATUS),
    ("CHL", datetime.date(1995, 3, 22), UNTC_UNFCCC_STATUS),
    ("BHR", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("KWT", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("MLI", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("RUS", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("SAU", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("SLB", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("THA", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("VEN", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("LAO", datetime.date(1995, 4, 4), UNTC_UNFCCC_STATUS),
    ("JAM", datetime.date(1995, 4, 6), UNTC_UNFCCC_STATUS),
    ("COD", datetime.date(1995, 4, 9), UNTC_UNFCCC_STATUS),
    ("KIR", datetime.date(1995, 5, 8), UNTC_UNFCCC_STATUS),
    ("LSO", datetime.date(1995, 5, 8), UNTC_UNFCCC_STATUS),
    ("OMN", datetime.date(1995, 5, 9), UNTC_UNFCCC_STATUS),
    ("TGO", datetime.date(1995, 6, 6), UNTC_UNFCCC_STATUS),
    ("CAF", datetime.date(1995, 6, 8), UNTC_UNFCCC_STATUS),
    ("COL", datetime.date(1995, 6, 20), UNTC_UNFCCC_STATUS),
    ("LVA", datetime.date(1995, 6, 21), UNTC_UNFCCC_STATUS),
    ("LTU", datetime.date(1995, 6, 22), UNTC_UNFCCC_STATUS),
    ("CPV", datetime.date(1995, 6, 27), UNTC_UNFCCC_STATUS),
    ("ERI", datetime.date(1995, 7, 23), UNTC_UNFCCC_STATUS),
    ("BGR", datetime.date(1995, 8, 10), UNTC_UNFCCC_STATUS),
    ("AZE", datetime.date(1995, 8, 14), UNTC_UNFCCC_STATUS),
    ("NAM", datetime.date(1995, 8, 14), UNTC_UNFCCC_STATUS),
    ("KAZ", datetime.date(1995, 8, 15), UNTC_UNFCCC_STATUS),
    ("PAN", datetime.date(1995, 8, 21), UNTC_UNFCCC_STATUS),
    ("TKM", datetime.date(1995, 9, 3), UNTC_UNFCCC_STATUS),
    ("MDA", datetime.date(1995, 9, 7), UNTC_UNFCCC_STATUS),
    ("SLE", datetime.date(1995, 9, 20), UNTC_UNFCCC_STATUS),
    ("NER", datetime.date(1995, 10, 23), UNTC_UNFCCC_STATUS),
    ("BTN", datetime.date(1995, 11, 23), UNTC_UNFCCC_STATUS),
    ("MOZ", datetime.date(1995, 11, 23), UNTC_UNFCCC_STATUS),
    ("DJI", datetime.date(1995, 11, 25), UNTC_UNFCCC_STATUS),
    ("GHA", datetime.date(1995, 12, 5), UNTC_UNFCCC_STATUS),
    ("HND", datetime.date(1996, 1, 17), UNTC_UNFCCC_STATUS),
    ("GNB", datetime.date(1996, 1, 25), UNTC_UNFCCC_STATUS),
    ("NIC", datetime.date(1996, 1, 29), UNTC_UNFCCC_STATUS),
    ("SVN", datetime.date(1996, 2, 29), UNTC_UNFCCC_STATUS),
    ("SLV", datetime.date(1996, 3, 3), UNTC_UNFCCC_STATUS),
    ("GTM", datetime.date(1996, 3, 14), UNTC_UNFCCC_STATUS),
    ("KHM", datetime.date(1996, 3, 17), UNTC_UNFCCC_STATUS),
    ("MAR", datetime.date(1996, 3, 27), UNTC_UNFCCC_STATUS),
    ("ARE", datetime.date(1996, 3, 28), UNTC_UNFCCC_STATUS),
    ("SYR", datetime.date(1996, 4, 3), UNTC_UNFCCC_STATUS),
    ("BEL", datetime.date(1996, 4, 15), UNTC_UNFCCC_STATUS),
    ("YEM", datetime.date(1996, 5, 21), UNTC_UNFCCC_STATUS),
    ("NIU", datetime.date(1996, 5, 28), UNTC_UNFCCC_STATUS),
    ("HRV", datetime.date(1996, 7, 7), UNTC_UNFCCC_STATUS),
    ("TZA", datetime.date(1996, 7, 16), UNTC_UNFCCC_STATUS),
    ("QAT", datetime.date(1996, 7, 17), UNTC_UNFCCC_STATUS),
    ("ISR", datetime.date(1996, 9, 2), UNTC_UNFCCC_STATUS),
    ("IRN", datetime.date(1996, 10, 16), UNTC_UNFCCC_STATUS),
    ("HTI", datetime.date(1996, 12, 24), UNTC_UNFCCC_STATUS),
    ("SWZ", datetime.date(1997, 1, 5), UNTC_UNFCCC_STATUS),
    ("COG", datetime.date(1997, 1, 12), UNTC_UNFCCC_STATUS),
    ("VCT", datetime.date(1997, 3, 2), UNTC_UNFCCC_STATUS),
    ("BDI", datetime.date(1997, 4, 6), UNTC_UNFCCC_STATUS),
    ("UKR", datetime.date(1997, 8, 11), UNTC_UNFCCC_STATUS),
    ("SGP", datetime.date(1997, 8, 27), UNTC_UNFCCC_STATUS),
    ("ZAF", datetime.date(1997, 11, 27), UNTC_UNFCCC_STATUS),
    ("SUR", datetime.date(1998, 1, 12), UNTC_UNFCCC_STATUS),
    ("CYP", datetime.date(1998, 1, 13), UNTC_UNFCCC_STATUS),
    ("TJK", datetime.date(1998, 4, 7), UNTC_UNFCCC_STATUS),
    ("GAB", datetime.date(1998, 4, 21), UNTC_UNFCCC_STATUS),
    ("MKD", datetime.date(1998, 4, 28), UNTC_UNFCCC_STATUS),
    ("TON", datetime.date(1998, 10, 18), UNTC_UNFCCC_STATUS),
    ("RWA", datetime.date(1998, 11, 16), UNTC_UNFCCC_STATUS),
    ("DOM", datetime.date(1999, 1, 5), UNTC_UNFCCC_STATUS),
    ("MDG", datetime.date(1999, 8, 31), UNTC_UNFCCC_STATUS),
    ("LBY", datetime.date(1999, 9, 12), UNTC_UNFCCC_STATUS),
    ("STP", datetime.date(1999, 12, 28), UNTC_UNFCCC_STATUS),
    ("PLW", datetime.date(2000, 3, 9), UNTC_UNFCCC_STATUS),
    ("BLR", datetime.date(2000, 8, 9), UNTC_UNFCCC_STATUS),
    ("AGO", datetime.date(2000, 8, 15), UNTC_UNFCCC_STATUS),
    ("KGZ", datetime.date(2000, 8, 23), UNTC_UNFCCC_STATUS),
    ("GNQ", datetime.date(2000, 11, 14), UNTC_UNFCCC_STATUS),
    ("BIH", datetime.date(2000, 12, 6), UNTC_UNFCCC_STATUS),
    (
        "SRB",
        datetime.date(2001, 6, 10),
        "https://treaties.un.org/doc/Publication/CN/2001/CN.283.2001-Eng.pdf",
    ),
    (
        "AFG",
        datetime.date(2002, 12, 18),
        "https://treaties.un.org/doc/Publication/CN/2002/CN.1019.2002-Eng.pdf",
    ),
    (
        "LBR",
        datetime.date(2003, 2, 3),
        "https://treaties.un.org/doc/Publication/CN/2002/CN.1165.2002-Eng.pdf",
    ),
    (
        "TUR",
        datetime.date(2004, 5, 24),
        "https://treaties.un.org/doc/Publication/CN/2004/CN.154.2004-Eng.pdf",
    ),
    (
        "MNE",
        datetime.date(2006, 6, 3),
        "https://treaties.un.org/doc/Publication/CN/2006/CN.1359.2006-Eng.pdf",
    ),
    (
        "TLS",
        datetime.date(2007, 1, 8),
        "https://treaties.un.org/doc/Publication/CN/2006/CN.830.2006-Eng.pdf",
    ),
    (
        "BRN",
        datetime.date(2007, 11, 5),
        "https://treaties.un.org/doc/Publication/CN/2007/CN.801.2007-Eng.pdf",
    ),
    (
        "IRQ",
        datetime.date(2009, 10, 26),
        "https://treaties.un.org/doc/Publication/CN/2009/CN.488.2009-Eng.pdf",
    ),
    (
        "SOM",
        datetime.date(2009, 12, 10),
        "https://treaties.un.org/doc/Publication/CN/2009/CN.734.2009-Eng.pdf",
    ),
    (
        "AND",
        datetime.date(2011, 5, 31),
        "https://treaties.un.org/doc/Publication/CN/2011/CN.90.2011-Eng.pdf",
    ),
    (
        "SSD",
        datetime.date(2014, 5, 18),
        "https://treaties.un.org/doc/Publication/CN/2014/CN.91.2014-Eng.pdf",
    ),
    (
        "PSE",
        datetime.date(2016, 3, 17),
        "https://treaties.un.org/doc/Publication/CN/2015/CN.699.2015-Eng.pdf",
    ),
    (
        "VAT",
        datetime.date(2022, 10, 4),
        "https://treaties.un.org/doc/Publication/CN/2022/CN.184.2022-Eng.pdf",
    ),
]

# Parties which withdrew from the UNFCCC, with the date on which the withdrawal took
# effect according to article 25 of the Convention, and the depositary notification.
UNFCCC_LEFT: list[tuple[str, datetime.date, str]] = [
    (
        "USA",
        datetime.date(2027, 2, 27),
        "https://treaties.un.org/doc/Publication/CN/2026/CN.102.2026-Eng.pdf",
    ),
]

# Status of the Paris Agreement at its depositary, the Secretary-General of the United
# Nations. Lists the date on which every party deposited its instrument of
# ratification, acceptance, approval, or accession.
UNTC_PARIS_STATUS = (
    "https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVII-7-d"
    "&chapter=27&clang=_en"
)

# Parties to the Paris Agreement with the date on which the Agreement entered into
# force for them and a reference for it, in the order in which they joined. According
# to article 21 of the Agreement
# (https://unfccc.int/sites/default/files/english_paris_agreement.pdf), the Agreement
# entered into force on 2016-11-04 for all parties which deposited their instrument
# until 2016-10-05, and enters into force 30 days after the deposit for all later
# parties. We give the depositary's status page as reference, except for the USA,
# which joined twice, for which we give the depositary notifications.
PARIS_JOINED: list[tuple[str, datetime.date, str]] = [
    ("ALB", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("ARE", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("ARG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("ATG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("AUT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BGD", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BHS", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BLR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BLZ", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BOL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BRA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BRB", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BRN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("CAN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("CHN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("CMR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("COK", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("DEU", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("DMA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("EU", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("FJI", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("FRA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("FSM", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("GHA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("GIN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("GRD", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("GUY", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("HND", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("HUN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("IND", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("ISL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("KIR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("KNA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("LAO", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("LCA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("LKA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MAR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MDG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MDV", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MEX", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MHL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MLI", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MLT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MNG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MUS", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NAM", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NER", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NOR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NPL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NRU", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NZL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PAN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PER", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PLW", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PNG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PRK", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PRT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PSE", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SEN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SGP", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SLB", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SOM", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SVK", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SWZ", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SYC", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("THA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("TON", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("TUV", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("UGA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("UKR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    (
        "USA",
        datetime.date(2016, 11, 4),
        "https://treaties.un.org/doc/Publication/CN/2016/CN.612.2016-Eng.pdf",
    ),
    ("VCT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("VUT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("WSM", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("RWA", datetime.date(2016, 11, 5), UNTC_PARIS_STATUS),
    ("POL", datetime.date(2016, 11, 6), UNTC_PARIS_STATUS),
    ("CAF", datetime.date(2016, 11, 10), UNTC_PARIS_STATUS),
    ("CRI", datetime.date(2016, 11, 12), UNTC_PARIS_STATUS),
    ("SWE", datetime.date(2016, 11, 12), UNTC_PARIS_STATUS),
    ("GRC", datetime.date(2016, 11, 13), UNTC_PARIS_STATUS),
    ("PRY", datetime.date(2016, 11, 13), UNTC_PARIS_STATUS),
    ("URY", datetime.date(2016, 11, 18), UNTC_PARIS_STATUS),
    ("DZA", datetime.date(2016, 11, 19), UNTC_PARIS_STATUS),
    ("TKM", datetime.date(2016, 11, 19), UNTC_PARIS_STATUS),
    ("MCO", datetime.date(2016, 11, 23), UNTC_PARIS_STATUS),
    ("CIV", datetime.date(2016, 11, 24), UNTC_PARIS_STATUS),
    ("NIU", datetime.date(2016, 11, 27), UNTC_PARIS_STATUS),
    ("BEN", datetime.date(2016, 11, 30), UNTC_PARIS_STATUS),
    ("IDN", datetime.date(2016, 11, 30), UNTC_PARIS_STATUS),
    ("DNK", datetime.date(2016, 12, 1), UNTC_PARIS_STATUS),
    ("SLE", datetime.date(2016, 12, 1), UNTC_PARIS_STATUS),
    ("ZAF", datetime.date(2016, 12, 1), UNTC_PARIS_STATUS),
    ("GAB", datetime.date(2016, 12, 2), UNTC_PARIS_STATUS),
    ("STP", datetime.date(2016, 12, 2), UNTC_PARIS_STATUS),
    ("KOR", datetime.date(2016, 12, 3), UNTC_PARIS_STATUS),
    ("SAU", datetime.date(2016, 12, 3), UNTC_PARIS_STATUS),
    ("VNM", datetime.date(2016, 12, 3), UNTC_PARIS_STATUS),
    ("EST", datetime.date(2016, 12, 4), UNTC_PARIS_STATUS),
    ("IRL", datetime.date(2016, 12, 4), UNTC_PARIS_STATUS),
    ("JOR", datetime.date(2016, 12, 4), UNTC_PARIS_STATUS),
    ("LUX", datetime.date(2016, 12, 4), UNTC_PARIS_STATUS),
    ("GMB", datetime.date(2016, 12, 7), UNTC_PARIS_STATUS),
    ("JPN", datetime.date(2016, 12, 8), UNTC_PARIS_STATUS),
    ("AUS", datetime.date(2016, 12, 9), UNTC_PARIS_STATUS),
    ("PAK", datetime.date(2016, 12, 10), UNTC_PARIS_STATUS),
    ("BFA", datetime.date(2016, 12, 11), UNTC_PARIS_STATUS),
    ("BWA", datetime.date(2016, 12, 11), UNTC_PARIS_STATUS),
    ("DJI", datetime.date(2016, 12, 11), UNTC_PARIS_STATUS),
    ("ITA", datetime.date(2016, 12, 11), UNTC_PARIS_STATUS),
    ("FIN", datetime.date(2016, 12, 14), UNTC_PARIS_STATUS),
    ("MYS", datetime.date(2016, 12, 16), UNTC_PARIS_STATUS),
    ("GBR", datetime.date(2016, 12, 18), UNTC_PARIS_STATUS),
    ("ISR", datetime.date(2016, 12, 22), UNTC_PARIS_STATUS),
    ("COM", datetime.date(2016, 12, 23), UNTC_PARIS_STATUS),
    ("BGR", datetime.date(2016, 12, 29), UNTC_PARIS_STATUS),
    ("KAZ", datetime.date(2017, 1, 5), UNTC_PARIS_STATUS),
    ("ZMB", datetime.date(2017, 1, 8), UNTC_PARIS_STATUS),
    ("SVN", datetime.date(2017, 1, 15), UNTC_PARIS_STATUS),
    ("BHR", datetime.date(2017, 1, 22), UNTC_PARIS_STATUS),
    ("CUB", datetime.date(2017, 1, 27), UNTC_PARIS_STATUS),
    ("KEN", datetime.date(2017, 1, 27), UNTC_PARIS_STATUS),
    ("CYP", datetime.date(2017, 2, 3), UNTC_PARIS_STATUS),
    ("AZE", datetime.date(2017, 2, 8), UNTC_PARIS_STATUS),
    ("ESP", datetime.date(2017, 2, 11), UNTC_PARIS_STATUS),
    ("TCD", datetime.date(2017, 2, 11), UNTC_PARIS_STATUS),
    ("LSO", datetime.date(2017, 2, 19), UNTC_PARIS_STATUS),
    ("GTM", datetime.date(2017, 2, 24), UNTC_PARIS_STATUS),
    ("LTU", datetime.date(2017, 3, 4), UNTC_PARIS_STATUS),
    ("KHM", datetime.date(2017, 3, 8), UNTC_PARIS_STATUS),
    ("CHL", datetime.date(2017, 3, 12), UNTC_PARIS_STATUS),
    ("TUN", datetime.date(2017, 3, 12), UNTC_PARIS_STATUS),
    ("AFG", datetime.date(2017, 3, 17), UNTC_PARIS_STATUS),
    ("MRT", datetime.date(2017, 3, 29), UNTC_PARIS_STATUS),
    ("ETH", datetime.date(2017, 4, 8), UNTC_PARIS_STATUS),
    ("BIH", datetime.date(2017, 4, 15), UNTC_PARIS_STATUS),
    ("LVA", datetime.date(2017, 4, 15), UNTC_PARIS_STATUS),
    ("TJK", datetime.date(2017, 4, 21), UNTC_PARIS_STATUS),
    ("ARM", datetime.date(2017, 4, 22), UNTC_PARIS_STATUS),
    ("PHL", datetime.date(2017, 4, 22), UNTC_PARIS_STATUS),
    ("AND", datetime.date(2017, 4, 23), UNTC_PARIS_STATUS),
    ("SLV", datetime.date(2017, 4, 26), UNTC_PARIS_STATUS),
    ("BEL", datetime.date(2017, 5, 6), UNTC_PARIS_STATUS),
    ("JAM", datetime.date(2017, 5, 10), UNTC_PARIS_STATUS),
    ("COG", datetime.date(2017, 5, 21), UNTC_PARIS_STATUS),
    ("GEO", datetime.date(2017, 6, 7), UNTC_PARIS_STATUS),
    ("NGA", datetime.date(2017, 6, 15), UNTC_PARIS_STATUS),
    ("HRV", datetime.date(2017, 6, 23), UNTC_PARIS_STATUS),
    ("ROU", datetime.date(2017, 7, 1), UNTC_PARIS_STATUS),
    ("MDA", datetime.date(2017, 7, 20), UNTC_PARIS_STATUS),
    ("QAT", datetime.date(2017, 7, 23), UNTC_PARIS_STATUS),
    ("TGO", datetime.date(2017, 7, 28), UNTC_PARIS_STATUS),
    ("EGY", datetime.date(2017, 7, 29), UNTC_PARIS_STATUS),
    ("MWI", datetime.date(2017, 7, 29), UNTC_PARIS_STATUS),
    ("VEN", datetime.date(2017, 8, 20), UNTC_PARIS_STATUS),
    ("SRB", datetime.date(2017, 8, 24), UNTC_PARIS_STATUS),
    ("NLD", datetime.date(2017, 8, 27), UNTC_PARIS_STATUS),
    ("HTI", datetime.date(2017, 8, 30), UNTC_PARIS_STATUS),
    ("SDN", datetime.date(2017, 9, 1), UNTC_PARIS_STATUS),
    ("ZWE", datetime.date(2017, 9, 6), UNTC_PARIS_STATUS),
    ("TLS", datetime.date(2017, 9, 15), UNTC_PARIS_STATUS),
    ("BTN", datetime.date(2017, 10, 19), UNTC_PARIS_STATUS),
    ("MMR", datetime.date(2017, 10, 19), UNTC_PARIS_STATUS),
    ("ECU", datetime.date(2017, 10, 20), UNTC_PARIS_STATUS),
    ("LIE", datetime.date(2017, 10, 20), UNTC_PARIS_STATUS),
    ("CPV", datetime.date(2017, 10, 21), UNTC_PARIS_STATUS),
    ("DOM", datetime.date(2017, 10, 21), UNTC_PARIS_STATUS),
    ("CZE", datetime.date(2017, 11, 4), UNTC_PARIS_STATUS),
    ("CHE", datetime.date(2017, 11, 5), UNTC_PARIS_STATUS),
    ("NIC", datetime.date(2017, 11, 22), UNTC_PARIS_STATUS),
    ("SYR", datetime.date(2017, 12, 13), UNTC_PARIS_STATUS),
    ("COD", datetime.date(2018, 1, 12), UNTC_PARIS_STATUS),
    ("MNE", datetime.date(2018, 1, 19), UNTC_PARIS_STATUS),
    ("MKD", datetime.date(2018, 2, 8), UNTC_PARIS_STATUS),
    ("BDI", datetime.date(2018, 2, 16), UNTC_PARIS_STATUS),
    ("TTO", datetime.date(2018, 3, 24), UNTC_PARIS_STATUS),
    ("KWT", datetime.date(2018, 5, 23), UNTC_PARIS_STATUS),
    ("TZA", datetime.date(2018, 6, 17), UNTC_PARIS_STATUS),
    ("MOZ", datetime.date(2018, 7, 4), UNTC_PARIS_STATUS),
    ("COL", datetime.date(2018, 8, 11), UNTC_PARIS_STATUS),
    ("LBR", datetime.date(2018, 9, 26), UNTC_PARIS_STATUS),
    ("SMR", datetime.date(2018, 10, 26), UNTC_PARIS_STATUS),
    ("GNB", datetime.date(2018, 11, 21), UNTC_PARIS_STATUS),
    ("GNQ", datetime.date(2018, 11, 29), UNTC_PARIS_STATUS),
    ("UZB", datetime.date(2018, 12, 9), UNTC_PARIS_STATUS),
    ("SUR", datetime.date(2019, 3, 15), UNTC_PARIS_STATUS),
    ("OMN", datetime.date(2019, 6, 21), UNTC_PARIS_STATUS),
    ("RUS", datetime.date(2019, 11, 6), UNTC_PARIS_STATUS),
    ("LBN", datetime.date(2020, 3, 6), UNTC_PARIS_STATUS),
    ("KGZ", datetime.date(2020, 3, 19), UNTC_PARIS_STATUS),
    ("AGO", datetime.date(2020, 12, 16), UNTC_PARIS_STATUS),
    (
        "USA",
        datetime.date(2021, 2, 19),
        "https://treaties.un.org/doc/Publication/CN/2021/CN.10.2021-Eng.pdf",
    ),
    ("SSD", datetime.date(2021, 3, 25), UNTC_PARIS_STATUS),
    ("TUR", datetime.date(2021, 11, 10), UNTC_PARIS_STATUS),
    ("IRQ", datetime.date(2021, 12, 1), UNTC_PARIS_STATUS),
    ("VAT", datetime.date(2022, 10, 4), UNTC_PARIS_STATUS),
    ("ERI", datetime.date(2023, 3, 9), UNTC_PARIS_STATUS),
]

# Parties which withdrew from the Paris Agreement, with the date on which the
# withdrawal took effect according to article 28 of the Agreement, and the depositary
# notification.
PARIS_LEFT: list[tuple[str, datetime.date, str]] = [
    (
        "USA",
        datetime.date(2020, 11, 4),
        "https://treaties.un.org/doc/Publication/CN/2019/CN.575.2019-Eng.pdf",
    ),
    (
        "USA",
        datetime.date(2026, 1, 27),
        "https://treaties.un.org/doc/Publication/CN/2025/CN.71.2025-Eng.pdf",
    ),
]


def main():
    """Generate the categorization."""

    categories = load_countries()

    # add some widely used additional categories
    categories["World"] = {
        "title": "The world",
        "alternative_codes": ["EARTH", "Earth", "WORLD"],
        "children": [list(categories.keys())],
    }
    categories = add_eu_categories(categories)
    categories = add_unfccc_categories(categories)
    categories = add_unfccc_versions(categories)
    categories = add_paris_categories(categories)
    categories = add_unfccc_names(categories)
    categories = add_aosis(categories)
    categories = add_g7g20(categories)
    categories = add_oecd(categories)
    categories = add_historical_names(categories)
    categories = add_basic(categories)
    categories = add_ldc(categories)
    categories = add_umbrella(categories)
    categories = add_OPEC(categories)
    categories = add_ARAB(categories)
    categories = add_LMDC(categories)
    categories = add_G35(categories)

    spec = {
        "name": "ISO3",
        "title": "ISO 3166-1 countries with climate-relevant groupings",
        "comment": "Countries, regions, and other areas. Also includes information on "
        "groups like being included in Annex I of the UN Framework Convention on "
        "Climate Change.",
        "references": """ISO 3166, https://www.iso.org/iso-3166-country-codes.html;
iso-codes package, https://salsa.debian.org/iso-codes-team/iso-codes;
UNFCCC Parties & Observers, https://unfccc.int/parties-observers;
UNFCCC status at the depositary,
https://treaties.un.org/Pages/ViewDetailsIII.aspx?src=TREATY&mtdsg_no=XXVII-7&chapter=27&Temp=mtdsg3&clang=_en;
Paris Agreement status at the depositary,
https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVII-7-d&chapter=27&clang=_en;
EU members,
https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:EU_enlargements;
G7 and G20, https://www.bmuv.de/themen/europa-internationales/internationales/g7-und-g20;
OECD members, https://www.oecd.org/about/document/ratification-oecd-convention.htm;
UMBRELLA https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/parties/party-groupings;
LDC https://www.un.org/development/desa/dpad/wp-content/uploads/sites/45/publication/ldc_list.pdf;
AOSIS members, https://www.aosis.org/about/member-states/;
OPEC https://www.opec.org/member-countries.html";
ARAB https://unfccc.int/party-groupings;
LMDC https://en.wikipedia.org/wiki/Like-Minded_Developing_Countries;
""",
        "institution": "UN",
        "last_update": LAST_UPDATE.isoformat(),
        "hierarchical": True,
        "version": LAST_UPDATE.isoformat(),
        "total_sum": False,
        "categories": categories,
        "canonical_top_level_category": "WORLD",
    }

    return climate_categories.HierarchicalCategorization.from_spec(spec)


def add_basic(categories):
    categories["BASIC"] = {
        "title": "BASIC countries",
        "children": [["BRA", "ZAF", "IND", "CHN"]],
    }
    return categories


def add_ldc(categories):
    categories["LDC"] = {
        "title": "Least Developed Countries",
        "children": [
            [
                "AGO",
                "BEN",
                "BFA",
                "BDI",
                "CAF",
                "TCD",
                "COM",
                "COD",
                "DJI",
                "ERI",
                "ETH",
                "GMB",
                "GIN",
                "GNB",
                "LSO",
                "LBR",
                "MDG",
                "MWI",
                "MLI",
                "MRT",
                "MOZ",
                "NER",
                "RWA",
                "SEN",
                "SLE",
                "SOM",
                "SSD",
                "SDN",
                "TGO",
                "UGA",
                "TZA",
                "ZMB",
                "AFG",
                "BGD",
                "KHM",
                "LAO",
                "MMR",
                "NPL",
                "TLS",
                "YEM",
                "HTI",
                "KIR",
                "SLB",
                "TUV",
            ]
        ],
    }
    return categories


def add_umbrella(categories):
    categories["UMBRELLA_2023"] = {
        "title": "The Umbrella Group",
        "comment": "The Umbrella Group is a coalition of Parties which formed following the adoption of the Kyoto Protocol. The United Kingdom formally joined the group in 2023.",
        "children": [
            [
                "AUS",
                "CAN",
                "ISL",
                "ISR",
                "JPN",
                "NZL",
                "KAZ",
                "NOR",
                "UKR",
                "USA",
                "GBR",
            ]
        ],
        "alternative_codes": ["UMBRELLA"],
    }
    return categories


def add_aosis(categories):
    categories["AOSIS"] = {
        "title": "Alliance of Small Island States",
        "children": [
            [
                "ATG",
                "BHS",
                "BRB",
                "BLZ",
                "CUB",
                "DMA",
                "DOM",
                "GRD",
                "GUY",
                "HTI",
                "JAM",
                "KNA",
                "LCA",
                "VCT",
                "SUR",
                "TTO",
                "COK",
                "FSM",
                "FJI",
                "KIR",
                "NRU",
                "NIU",
                "PLW",
                "PNG",
                "MHL",
                "WSM",
                "SLB",
                "TON",
                "TUV",
                "VUT",
                "CPV",
                "COM",
                "GNB",
                "MDV",
                "MUS",
                "STP",
                "SYC",
                "SGP",
                "TLS",
            ]
        ],
    }
    return categories


def add_OPEC(categories):
    categories["OPEC"] = {
        "title": "Oranization of Petroleum Exporting Countries",
        "children": [
            [
                "IRN",
                "IRQ",
                "KWT",
                "SAU",
                "VEN",
                "LBY",
                "ARE",
                "DZA",
                "NGA",
                "GAB",
                "GNQ",
                "COG",
            ]
        ],
    }
    return categories


def add_ARAB(categories):
    categories["ARAB"] = {
        "title": "Arab Group",
        "children": [
            [
                "DZA",
                "BHR",
                "COM",
                "DJI",
                "EGY",
                "IRQ",
                "JOR",
                "KWT",
                "LBN",
                "LBY",
                "MAR",
                "MRT",
                "OMN",
                "PSE",
                "QAT",
                "SAU",
                "SOM",
                "SDN",
                "SYR",
                "TUN",
                "ARE",
                "YEM",
            ]
        ],
    }
    return categories


def add_LMDC(categories):
    categories["LMDC"] = {
        "title": "Like-minded developing countries",
        "children": [
            [
                "DZA",
                "BGD",
                "BOL",
                "CHN",
                "CUB",
                "ECU",
                "EGY",
                "SLV",
                "IND",
                "IDN",
                "IRN",
                "IRQ",
                "JOR",
                "KWT",
                "MYS",
                "MLI",
                "NIC",
                "PAK",
                "SAU",
                "LKA",
                "SDN",
                "SYR",
                "VEN",
                "VNM",
            ]
        ],
    }
    return categories


def add_G35(categories):
    categories["G35"] = {
        "title": "Group of 35",
        "children": [
            [
                "ARG",
                "AUS",
                "AZE",
                "BRA",
                "CAN",
                "CHL",
                "CHN",
                "COL",
                "EGY",
                "FRA",
                "DEU",
                "IND",
                "IDN",
                "IRN",
                "ITA",
                "JPN",
                "KAZ",
                "KEN",
                "KOR",
                "MYS",
                "MEX",
                "MNG",
                "NGA",
                "PAK",
                "PHL",
                "RUS",
                "SAU",
                "ZAF",
                "THA",
                "TUR",
                "GBR",
                "ARE",
                "USA",
                "VNM",
                "AUT",
                "BEL",
                "BGR",
                "HRV",
                "CYP",
                "CZE",
                "DNK",
                "EST",
                "FIN",
                "GRC",
                "HUN",
                "IRL",
                "LVA",
                "LTU",
                "LUX",
                "MLT",
                "NLD",
                "POL",
                "PRT",
                "ROU",
                "SVK",
                "SVN",
                "ESP",
                "SWE",
            ]
        ],
    }
    return categories


def add_historical_names(categories):
    categories["TUR"]["info"]["historical_names"] = ["Turkey"]
    return categories


def add_oecd(categories):
    categories["OECD"] = {
        "title": "Organisation for Economic Co-operation and Development",
        "children": [
            [
                "AUS",
                "AUT",
                "BEL",
                "CAN",
                "CHL",
                "COL",
                "CRI",
                "CZE",
                "DNK",
                "EST",
                "FIN",
                "FRA",
                "DEU",
                "GRC",
                "HUN",
                "ISL",
                "IRL",
                "ISR",
                "ITA",
                "JPN",
                "KOR",
                "LVA",
                "LTU",
                "LUX",
                "MEX",
                "NLD",
                "NZL",
                "NOR",
                "POL",
                "PRT",
                "SVK",
                "SVN",
                "ESP",
                "SWE",
                "CHE",
                "TUR",
                "GBR",
                "USA",
            ]
        ],
    }
    return categories


def add_g7g20(categories):
    categories["G7"] = {
        "title": "Group of Seven",
        "children": [["DEU", "FRA", "GBR", "ITA", "JPN", "USA", "CAN", "EU"]],
    }
    categories["G8"] = {
        "title": "Group of Eight",
        "children": [categories["G7"]["children"][0] + ["RUS"]],
    }
    categories["G20"] = {
        "title": "Group of 20",
        "children": [
            categories["G8"]["children"][0]
            + [
                "ARG",
                "AUS",
                "BRA",
                "CHN",
                "IND",
                "IDN",
                "MEX",
                "SAU",
                "ZAF",
                "KOR",
                "TUR",
            ]
        ],
    }
    return categories


def add_unfccc_names(categories):
    categories["BOL"]["info"]["unfccc_name"] = "Bolivia (Plurinational State of)"
    categories["COD"]["info"] = {"unfccc_name": "Democratic Republic of the Congo"}
    categories["VAT"]["info"] = {"unfccc_name": "Holy See"}
    categories["IRN"]["info"]["unfccc_name"] = "Iran (Islamic Republic of)"
    categories["FSM"]["info"]["unfccc_name"] = "Micronesia (Federated States of)"
    categories["KOR"]["info"]["unfccc_name"] = "Republic of Korea"
    categories["PSE"]["info"]["unfccc_name"] = "State of Palestine"
    categories["VEN"]["info"]["unfccc_name"] = "Venezuela (Bolivarian Republic of)"
    return categories


def add_unfccc_categories(categories):
    categories["Annex-I"] = {
        "title": "Annex-I parties to the UNFCCC",
        "comment": "Parties to the UN Framework Convention on Climate Change "
        "listed in Annex I of the Convention.",
        "alternative_codes": ["ANNEXI"],
        "children": [
            [
                "AUS",
                "AUT",
                "BLR",
                "BEL",
                "BGR",
                "CAN",
                "HRV",
                "CYP",
                "CZE",
                "DNK",
                "EST",
                "FIN",
                "FRA",
                "DEU",
                "GRC",
                "HUN",
                "ISL",
                "IRL",
                "ITA",
                "JPN",
                "LVA",
                "LIE",
                "LTU",
                "LUX",
                "MLT",
                "MCO",
                "NLD",
                "NZL",
                "NOR",
                "POL",
                "PRT",
                "ROU",
                "RUS",
                "SVK",
                "SVN",
                "ESP",
                "SWE",
                "CHE",
                "TUR",
                "UKR",
                "GBR",
                "USA",
                "EU",
            ]
        ],
    }
    categories["Non-Annex-I"] = {
        "title": "Non-Annex-I parties to the UNFCCC",
        "comment": "Parties to the UN Framework Convention on Climate Change "
        "not listed in Annex I of the Convention.",
        "alternative_codes": ["NONANNEXI", "Non Annex-I"],
        "children": [
            [
                "AFG",
                "ALB",
                "DZA",
                "AND",
                "AGO",
                "ATG",
                "ARG",
                "ARM",
                "AZE",
                "BHS",
                "BHR",
                "BGD",
                "BRB",
                "BLZ",
                "BEN",
                "BTN",
                "BIH",
                "BWA",
                "BRA",
                "BRN",
                "BFA",
                "BDI",
                "CPV",
                "KHM",
                "CMR",
                "CAF",
                "TCD",
                "CHL",
                "CHN",
                "COL",
                "COM",
                "COG",
                "COK",
                "CRI",
                "CIV",
                "CUB",
                "DJI",
                "DMA",
                "DOM",
                "ECU",
                "EGY",
                "SLV",
                "GNQ",
                "ERI",
                "SWZ",
                "ETH",
                "FJI",
                "GAB",
                "GMB",
                "GEO",
                "GHA",
                "GRD",
                "GTM",
                "GIN",
                "GNB",
                "GUY",
                "HTI",
                "HND",
                "IND",
                "IDN",
                "IRQ",
                "ISR",
                "JAM",
                "JOR",
                "KAZ",
                "KEN",
                "KIR",
                "KWT",
                "KGZ",
                "LAO",
                "LBN",
                "LSO",
                "LBR",
                "LBY",
                "MDG",
                "MWI",
                "MYS",
                "MDV",
                "MLI",
                "MHL",
                "MRT",
                "MUS",
                "MEX",
                "MNG",
                "MNE",
                "MAR",
                "MOZ",
                "MMR",
                "NAM",
                "NRU",
                "NPL",
                "NIC",
                "NER",
                "NGA",
                "NIU",
                "MKD",
                "OMN",
                "PAK",
                "PLW",
                "PAN",
                "PNG",
                "PRY",
                "PER",
                "PHL",
                "QAT",
                "RWA",
                "KNA",
                "LCA",
                "VCT",
                "WSM",
                "SMR",
                "STP",
                "SAU",
                "SEN",
                "SRB",
                "SYC",
                "SLE",
                "SGP",
                "SLB",
                "SOM",
                "ZAF",
                "SSD",
                "LKA",
                "SDN",
                "SUR",
                "SYR",
                "TJK",
                "THA",
                "TLS",
                "TGO",
                "TON",
                "TTO",
                "TUN",
                "TKM",
                "TUV",
                "UGA",
                "ARE",
                "URY",
                "UZB",
                "VUT",
                "VNM",
                "YEM",
                "ZMB",
                "ZWE",
                "PRK",
                "COD",
                "VAT",
                "IRN",
                "FSM",
                "KOR",
                "MDA",
                "PSE",
                "TZA",
                "VEN",
                "BOL",
            ]
        ],
    }
    categories["UNFCCC"] = {
        "title": "Parties to the UNFCCC",
        "comment": "Parties to the UN Framework Convention on Climate Change. Note "
        "that the 'UNFCCC' code will always refer to the current parties, use the "
        "UNFCCC_YYYY_MM or UNFCCC_YYYY codes for past months or years if you need a "
        "stable code.",
        "children": [
            categories["Annex-I"]["children"][0]
            + categories["Non-Annex-I"]["children"][0],
            ["Annex-I", "Non-Annex-I"],
        ],
    }

    return categories


def add_unfccc_versions(categories):
    """Add the parties to the UNFCCC over time, see add_party_versions."""
    categories = add_party_versions(
        categories,
        prefix="UNFCCC",
        joined=UNFCCC_JOINED,
        left=UNFCCC_LEFT,
        title_name="UNFCCC",
        comment_name="UN Framework Convention on Climate Change",
        instrument="Convention",
    )

    assert set(categories["UNFCCC_2022_10"]["children"][0]) == set(
        categories["UNFCCC"]["children"][0]
    )

    return categories


def add_paris_categories(categories):
    """Add the parties to the Paris Agreement, currently and over time."""
    categories = add_party_versions(
        categories,
        prefix="PARIS",
        joined=PARIS_JOINED,
        left=PARIS_LEFT,
        title_name="Paris Agreement",
        comment_name="Paris Agreement",
        instrument="Agreement",
    )

    parties = []
    for date, code, kind in party_changes(PARIS_JOINED, PARIS_LEFT):
        if date > LAST_UPDATE:
            break
        if kind == "joined":
            parties.append(code)
        else:
            parties.remove(code)
    categories["PARIS"] = {
        "title": "Parties to the Paris Agreement",
        "comment": "Parties to the Paris Agreement. Note that the 'PARIS' code will "
        "always refer to the current parties, use the PARIS_YYYY_MM or PARIS_YYYY "
        "codes for past months or years if you need a stable code.",
        "children": [sorted(parties)],
    }

    assert set(parties) == set(categories["PARIS_2026_01"]["children"][0])
    # all parties to the UNFCCC except the non-parties to the Paris Agreement
    assert set(parties) == set(categories["UNFCCC"]["children"][0]) - {
        "IRN",
        "LBY",
        "YEM",
        "USA",
    }

    return categories


def party_changes(
    joined: list[tuple[str, datetime.date, str]],
    left: list[tuple[str, datetime.date, str]],
) -> list[tuple[datetime.date, str, str]]:
    """All changes of the parties to a treaty as (date, code, kind), sorted by date."""
    return sorted(
        [(date, code, "joined") for code, date, _ in joined]
        + [(date, code, "left") for code, date, _ in left]
    )


def add_party_versions(
    categories,
    *,
    prefix: str,
    joined: list[tuple[str, datetime.date, str]],
    left: list[tuple[str, datetime.date, str]],
    title_name: str,
    comment_name: str,
    instrument: str,
):
    """Add the parties to a treaty over time.

    For every month in which parties joined or left, there is a category
    {prefix}_YYYY_MM containing the parties after all changes in that month took
    effect. The last category of every year additionally has the code {prefix}_YYYY.
    Codes for the current or future months or years are not stable yet because further
    changes could still take effect, which is noted in the comment.
    """
    months = [
        (month, list(month_changes))
        for month, month_changes in itertools.groupby(
            party_changes(joined, left),
            key=lambda change: (change[0].year, change[0].month),
        )
    ]

    known_codes = set(categories)
    for spec in categories.values():
        known_codes.update(spec.get("alternative_codes", []))

    parties = []
    for i, ((year, month), month_changes) in enumerate(months):
        for _, code, kind in month_changes:
            assert code in known_codes, code
            if kind == "joined":
                assert code not in parties, code
                parties.append(code)
            else:
                assert code in parties, code
                parties.remove(code)

        start = month_changes[-1][0]
        if i + 1 < len(months):
            next_month_changes = months[i + 1][1]
            end = next_month_changes[0][0] - datetime.timedelta(days=1)
            validity = f"from {start.isoformat()} to {end.isoformat()}"
        else:
            validity = f"since {start.isoformat()}"

        descriptions = []
        for kind in ("joined", "left"):
            changed = [
                f"{', '.join(code for _, code, _ in date_changes)} ({date.isoformat()})"
                for date, date_changes in itertools.groupby(
                    (change for change in month_changes if change[2] == kind),
                    key=lambda change: change[0],
                )
            ]
            if changed:
                descriptions.append(f"{kind}: {', '.join(changed)}")
        comment = (
            f"Parties to the {comment_name} {validity}. "
            f"Changes in {year}-{month:02}, {'; '.join(descriptions)}."
        )
        if i == 0:
            entry_into_force = month_changes[0][0]
            comment += (
                f" The {instrument} entered into force on "
                f"{entry_into_force.isoformat()}."
            )
        if len({date for date, _, _ in month_changes}) > 1:
            comment += (
                " The category contains the parties after all changes in "
                f"{year}-{month:02} took effect."
            )

        is_last_of_year = i + 1 == len(months) or months[i + 1][0][0] != year
        if (year, month) >= (LAST_UPDATE.year, LAST_UPDATE.month):
            comment += (
                f" Note that the codes {prefix}_{year}_{month:02} and {prefix}_{year} "
                f"are not stable yet, further changes taking effect in "
                f"{year}-{month:02} or later in {year} would change the parties they "
                "refer to."
            )
        elif is_last_of_year and year >= LAST_UPDATE.year:
            comment += (
                f" Note that the code {prefix}_{year} is not stable yet, further "
                f"changes taking effect later in {year} would move it to a later "
                "category."
            )

        spec = {
            "title": f"Parties to the {title_name} {validity}",
            "comment": comment,
            "children": [parties.copy()],
        }
        if is_last_of_year:
            spec["alternative_codes"] = [f"{prefix}_{year}"]
        categories[f"{prefix}_{year}_{month:02}"] = spec

    return categories


def add_eu_categories(categories):
    categories["EU_1993"] = {
        "title": "European Union from 1993 to 1994",
        "comment": "The European Union from 1993-11-1 to 1994-12-31.",
        "alternative_codes": ["EU12", "EU-12"],
        "children": [
            [
                "BEL",
                "DNK",
                "FRA",
                "DEU",
                "GRC",
                "IRL",
                "ITA",
                "LUX",
                "NLD",
                "PRT",
                "ESP",
                "GBR",
            ]
        ],
    }
    categories["EU_1995"] = {
        "title": "European Union from 1995 to 2004",
        "comment": "The European Union from 1995-01-01 to 2004-04-30.",
        "alternative_codes": ["EU15", "EU-15"],
        "children": [categories["EU_1993"]["children"][0] + ["AUT", "FIN", "SWE"]],
    }
    categories["EU_2004"] = {
        "title": "European Union from 2004 to 2006",
        "comment": "The European Union from 2004-05-01 to 2006-12-31.",
        "alternative_codes": ["EU25", "EU-25"],
        "children": [
            categories["EU_1995"]["children"][0]
            + ["CYP", "CZE", "EST", "HUN", "LVA", "LTU", "MLT", "POL", "SVK", "SVN"]
        ],
    }
    # Do not include EU27 as it is unclear what it means
    categories["EU_2007"] = {
        "title": "European Union from 2007 to 2013",
        "comment": "The European Union from 2007-01-01 to 2013-06-30.",
        "alternative_codes": ["EU27_2007", "EU-27_2007"],
        "children": [categories["EU_2004"]["children"][0] + ["BGR", "ROU"]],
    }
    categories["EU_2013"] = {
        "title": "European Union from 2013 to 2020",
        "comment": "The European Union from 2013-07-01 to 2020-01-31.",
        "alternative_codes": ["EU28", "EU-28"],
        "children": [categories["EU_2007"]["children"][0] + ["HRV"]],
    }
    eu2020_children = categories["EU_2013"]["children"][0].copy()
    eu2020_children.remove("GBR")
    # Do not include EU27 as it is unclear what it means
    categories["EU_2020"] = {
        "title": "European Union",
        "comment": "The European Union since 2020-02-01 to date. Note that the 'EU' "
        "code will always refer to the current EU, use EU_2020 if you need "
        "a stable code.",
        "alternative_codes": ["EU27_2020", "EU-27_2020", "EU", "EU27BX"],
        "children": [eu2020_children],
    }

    return categories


def load_countries() -> dict[str, str | dict[str, str] | list[str] | list[list[str]]]:
    """Load countries from the iso-codes debian package."""
    r = requests.get(
        URL,
        headers={"Accept": "application/json"},
    )

    categories: dict[str, str | dict[str, str]] = {}
    for country in r.json()["3166-1"]:
        country_spec = {
            "title": country["name"],
            "alternative_codes": [country["alpha_2"], country["numeric"]],
        }

        info = {}
        if "official_name" in country:
            info["official_name"] = country["official_name"]
        if "common_name" in country:
            info["common_name"] = country["common_name"]
        if info:
            country_spec["info"] = info

        categories[country["alpha_3"]] = country_spec

    return categories


if __name__ == "__main__":
    ISO3 = main()

    write_categorization(ISO3, OUTPATH)
