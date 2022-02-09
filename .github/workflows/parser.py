#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json

from datetime import datetime
from pdfminer import high_level

DATAPATH = os.path.dirname(os.path.abspath(__file__)) + os.sep + ".." + os.sep + ".." + os.sep + "data_BW" + os.sep
DATE_STR = datetime.fromtimestamp(datetime.now().timestamp()).strftime('%Y-%m-%d')
PDF_FILENAME = "BW_{}.pdf".format(DATE_STR)
JSON_FILENAME = "BW_{}.json".format(DATE_STR)
PDF_FULLNAME = DATAPATH + PDF_FILENAME
JSON_FULLNAME = DATAPATH + JSON_FILENAME

parsed_pdf = high_level.extract_text(PDF_FULLNAME, maxpages=1)

faelle = re.search("(Bestätigte Fälle).*\s\n(.*)", parsed_pdf)
verstoberne = re.search("(Verstorbene).*\s\n(.*)", parsed_pdf)
genesene = re.search("(Genesene).*\s\n(.*)", parsed_pdf)
min_einmal_geimpft = re.search("(Mindestens einmal Geimpfte).*\s\n(.*)\s\n(.*\))", parsed_pdf)
grundimmunisiert = re.search("(Grundimmunisiert).*\s\n(.*)\s\n(.*\))", parsed_pdf)
geboostert = re.search("(Auffrischimpfungen).*\s\n(.*)\s\n(.*\))", parsed_pdf)

parsed_json = {
    faelle.group(1) : faelle.group(2),
    verstoberne.group(1): verstoberne.group(2),
    genesene.group(1): genesene.group(2),
    min_einmal_geimpft.group(1) : '\n'.join(min_einmal_geimpft.group(2,3)),
    grundimmunisiert.group(1) : '\n'.join(grundimmunisiert.group(2,3)),
    geboostert.group(1): '\n'.join(geboostert.group(2,3))
}

with open(JSON_FULLNAME, 'w', encoding='utf-8') as fp:
    json.dump(parsed_json, fp)
