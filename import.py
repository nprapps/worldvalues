#!/usr/bin/env python

import csv
import dataset
from collections import OrderedDict

POSTGRES_URL = 'postgresql:///worldvalues'
db = dataset.connect(POSTGRES_URL)


def load_data():
    table = db['survey_responses']
    data = []
    schema_created = False

    with open('data/WV6_Data_r_v_2015_04_18.csv') as f:
        print "build data"
        reader = csv.reader(f)
        raw_headers = reader.next()

        headers = []
        for header in raw_headers[1:]:
            headers.append(header.lower())

        for row in reader:
            data.append(row)

            if not schema_created:
                schema_created = True
                processed_row = []
                for column in row[1:]:
                    processed_row.append(str(column))
                processed_dict = OrderedDict(zip(headers, processed_row))
                table.insert(processed_dict)
                db.query('delete from survey_responses')

    with open('data/WV6_Data_r_v_2015_04_18-clean.csv', 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(data)


def load_codebook():
    codebook_table = db['codebook']
    category_table = db['categories']
    with open('data/codebook.csv') as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        question = OrderedDict((
            ('question_id', row['VAR'].lower()),
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
                ('question_id', row['VAR'].lower()),
                ('code', str(code)),
                ('value', str(real_value)),
            ))
            category_table.insert(category_row)


if __name__ == '__main__':
    load_codebook()
    load_data()
