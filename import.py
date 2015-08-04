#!/usr/bin/env python

import csv
import dataset
from collections import OrderedDict
from joblib import Parallel, delayed

POSTGRES_URL = 'postgresql:///worldvalues'
db = dataset.connect(POSTGRES_URL)


def load_data():
    table = db['survey_responses']
    data = []

    with open('data/WV6_Data_r_v_2015_04_18.csv') as f:
        print "build data"
        reader = csv.DictReader(f)

        for row in reader:
            del row['']
            data.append(row)

    print "insert data"
    table.insert_many(data, 5000)

# Parallel version
#def load_data():
    #table = db['survey_responses']
    #data = []

    #with open('data/WV6_Data_r_v_2015_04_18.csv') as f:
        #print "build data"
        #raw_data = list(csv.DictReader(f))

        #Parallel(n_jobs=8, backend='threading')(delayed(_process_row)(table, row) for row in raw_data)


#def _process_row(table, row):
    #del row['']
    #table.insert(row)

def load_codebook():
    codebook_table = db['codebook']
    category_table = db['categories']
    with open('data/codebook.csv') as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        question = OrderedDict((
            ('question_id', row['VAR']),
            ('question', row['QUESTION']),
            ('label', row['LABEL']),
        ))
        db_id = codebook_table.insert(question)

        categories = row['CATEGORIES'].splitlines()
        for category in categories:
            try:
                code, middle_value, real_value = category.split('#')
            except ValueError:
                print 'skipped {0} due to country specific code'.format(row['VAR'])
            category_row = OrderedDict((
                ('db_id', db_id),
                ('question_id', row['VAR']),
                ('code', code),
                ('value', real_value),
            ))
            category_table.insert(category_row)


if __name__ == '__main__':
    #load_codebook()
    load_data()
