#!/usr/bin/env python

import csv
import dataset

POSTGRES_URL = 'postgresql:///worldvalues'
db = dataset.connect(POSTGRES_URL)

def load_data():
    with open('data/WV6_Data_r_v_2015_04_18.csv') as f:
        reader = csv.DictReader(f)

        for row in reader:
            print row['V3']

def load_codebook():
    codebook_table = db['codebook']
    category_table = db['categories']
    with open('data/codebook.csv') as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        question = {
            'question': row['QUESTION'],
            'label': row['LABEL'],
            'question_id': row['VAR'],
        }
        question_id = codebook_table.insert(question)

        categories = row['CATEGORIES'].splitlines()
        for category in categories:
            try:
                code, middle_value, real_value = category.split('#')
            except ValueError:
                print 'skipped {0} due to country specific code'.format(row['VAR'])
            category_row = {
                'question_id': question_id,
                'code': code,
                'value': real_value,
            }
            category_table.insert(category_row)

if __name__ == '__main__':
    load_codebook()