#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import dataset
from collections import OrderedDict

POSTGRES_URL = 'postgresql:///worldvalues'
db = dataset.connect(POSTGRES_URL)

QUESTION_TYPES = (
    ('mentioned', """1##Mentioned
2##Not mentioned"""),
    ('agree_3way', """1##Agree
2##Neither
3##Disagree"""),
    ('agree_4way', """1##Agree strongly
2##Agree
3##Disagree
4##Strongly disagree"""),
    ('likert', """2##2
3##3
4##4
5##5
6##6
7##7
8##8
9##9"""),
)


def clean_data():
    """
    Clean data and create schema
    """

    schema_created = False

    cleaned_file = open('data/WV6_Data_ascii_v_2015_04_18-clean.csv', 'w')
    writer = csv.writer(cleaned_file, quoting=csv.QUOTE_ALL)

    input_file = open('data/WV6_Data_ascii_v_2015_04_18.dat')
    reader = csv.reader(input_file)

    raw_headers = reader.next()

    # Process rows
    for row in reader:
        # Add row to cleaned CSV
        writer.writerow(row)

        # Create database schema from first row
        if not schema_created:
            create_schema(row, raw_headers)
            schema_created = True


def create_schema(row, raw_headers):
    """
    Create schema from a single row of data
    """
    table = db['survey_responses']

    # Clean headers
    headers = []
    for header in raw_headers[1:]:
        headers.append(header.lower())

    # Clean row
    processed_row = []
    for column in row[1:]:
        processed_row.append(str(column))

    # Insert row into tabel
    processed_dict = OrderedDict(zip(headers, processed_row))
    table.insert(processed_dict)

    # Clear out table
    db.query('delete from survey_responses')


def load_codebook():
    codebook_table = db['codebook']
    category_table = db['categories']
    with open('data/codebook.csv') as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        question_type = None
        for potential_question_type, categories in QUESTION_TYPES:
            if categories in row['CATEGORIES']:
                question_type = potential_question_type
                break

        question = OrderedDict((
            ('question_id', row['VAR'].lower()),
            ('question', row['QUESTION']),
            ('label', row['LABEL']),
            ('question_type', question_type),
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
    clean_data()
