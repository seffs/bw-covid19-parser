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

pdfplumber_settings = {
    "vertical_strategy": "text",
    "keep_blank_chars": True,
}

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
        for table in page.extract_tables(pdfplumber_settings):
            for row in table:
                for i in range(len(row)):
                    if row[i] and ('SK' in row[i] or 'LK' in row[i]):
                        #There are, of course, better ways to solve this
                        bericht_pro_LSK[row[i]] = dict()
                        confirmed_delta_index = i + 1
                        while(row[confirmed_delta_index] != '-' and not re.findall(r'\(\+(\s)*([0-9]+)\)', row[confirmed_delta_index])):
                            confirmed_delta_index += 1
                        confirmed_index = confirmed_delta_index - 1
                        while(confirmed_index > i and not re.findall(r'^\s*([0-9]+[\.,]?)+[0-9]\s*$', row[confirmed_index])):
                            confirmed_index -= 1
                        bericht_pro_LSK[row[i]]['Bestätigte Fälle'] = row[confirmed_index].replace('\n','\\n') + (
                            ' ' + row[confirmed_delta_index].replace('\n','\\n') if row[confirmed_delta_index] != '-' else '')
                        death_delta_index = confirmed_delta_index + 1
                        while(row[death_delta_index] != '-' and not re.findall(r'\(\+(\s)*([0-9]+)\)', row[death_delta_index])):
                            death_delta_index += 1
                        death_index = death_delta_index - 1
                        while(death_index > i and not re.findall(r'^\s*([0-9]+[\.,]?)+[0-9]\s*$', row[death_index])):
                            death_index -= 1
                        bericht_pro_LSK[row[i]]['Verstorbene'] = row[death_index].replace('\n','\\n') + (
                            ' ' + row[death_delta_index].replace('\n','\\n') if row[death_delta_index] != '-' else '')
                        bericht_pro_LSK[row[i]]['7-Tage-Inzidenz'] = row[-1]
                        break
    else:
        break

pdf.close()

parsed_json = {'State': bericht_fuer_BW, 'LSK': bericht_pro_LSK}

with open(JSON_FULLNAME, 'w') as fp:
    json.dump(parsed_json, fp)
