#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

from datetime import datetime
import pdfplumber

DATE_STR = datetime.fromtimestamp(datetime.now().timestamp()).strftime('')
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
                                    break
    elif page.page_number == 2:
        for table in page.extract_tables():
            for row in table:
                for i in range(len(row)):
                    if row[i] and (row[i].startswith('SK') or row[i].startswith('LK')):
                        bericht_pro_LSK[row[i]] = dict()
                        bericht_pro_LSK[row[i]]['Bestätigte Fälle'] = row[i+1] + ' ' + row[i+2]
                        bericht_pro_LSK[row[i]]['Verstorbene'] = row[i+4] + ' ' + row[i+5]
                        bericht_pro_LSK[row[i]]['7-Tage-Inzidenz'] = row[i+4] + ' ' + row[i+5]
                        break
    else:
        break

pdf.close()

parsed_json = {'State': bericht_fuer_BW, 'LSK': bericht_pro_LSK}

with open(JSON_FULLNAME, 'w') as fp:
    json.dump(parsed_json, fp)
