#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re

from datetime import datetime
import pdfplumber

DATAPATH = os.path.dirname(os.path.abspath(__file__)) + os.sep + ".." + os.sep + ".." + os.sep + "data_BW" + os.sep
DATE_STR = datetime.fromtimestamp(datetime.now().timestamp()).strftime('%Y-%m-%d')
PDF_FILENAME = "BW_{}.pdf".format(DATE_STR)
JSON_FILENAME = "BW_{}.json".format(DATE_STR)
PDF_FULLNAME = DATAPATH + PDF_FILENAME
JSON_FULLNAME = DATAPATH + JSON_FILENAME

pdf = pdfplumber.open(PDF_FULLNAME)

bericht_keywords = ['Bestätigte Fälle', 'Verstorbene', 'Genesene', 
                    'Mindestens einmal Geimpfte', 'Grundimmunisiert', 'Auffrischimpfungen',
                    '7-Tage-Inzidenz']
bericht_fuer_BW = dict()
bericht_pro_LSK = dict()

for page in pdf.pages:
    if page.page_number == 1:
        for table in page.extract_tables():
            if len(bericht_fuer_BW) == len(bericht_keywords):
                break
            else:
                for row in table:
                    for keyword in bericht_keywords:
                        if not bericht_fuer_BW.get(keyword):
                            for cell in row:
                                if cell and keyword in cell:
                                    bericht_fuer_BW[keyword] = cell.split('\n',1)[1]
                                    bericht_fuer_BW[keyword] = bericht_fuer_BW[keyword].replace('\n','\\n')
                                    break
    elif page.page_number == 2:
        page_text = page.extract_text()
        for line in page_text.split('\n'):
            if 'SK' in line or 'LK' in line:
                lks_stats = line.split('  ')
                lks_name = lks_stats[0].split('#')[0][:-1]
                lks_bestaetig = lks_stats[1] + (' ' + lks_stats[2] if lks_stats[2] != '-' else '')
                lks_todesfaelle = lks_stats[4] + (' ' + lks_stats[5] if lks_stats[5] != '-' else '')
                lks_inzidenz = lks_stats[7] 

                bericht_pro_LSK[lks_name] = dict()
                bericht_pro_LSK[lks_name]['Bestätigte Fälle'] = lks_bestaetig
                bericht_pro_LSK[lks_name]['Verstorbene'] = lks_todesfaelle
                bericht_pro_LSK[lks_name]['7-Tage-Inzidenz'] = lks_inzidenz
    else:
        break

pdf.close()

parsed_json = {'State': bericht_fuer_BW, 'LSK': bericht_pro_LSK}

with open(JSON_FULLNAME, 'w') as fp:
    json.dump(parsed_json, fp)
