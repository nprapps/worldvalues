#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import dataset

POSTGRES_URL = 'postgresql:///worldvalues'
db = dataset.connect(POSTGRES_URL)

ANALYSIS_QUESTIONS = ['v{0}'.format(i) for i in range(12,23)]
ANALYSIS_QUESTIONS += ['v45', 'v47', 'v48']
ANALYSIS_QUESTIONS += ['v{0}'.format(i) for i in range(50,55)]
ANALYSIS_QUESTIONS += ['v80', 'v123', 'v139', 'v168', 'v182', 'v203a']
ANALYSIS_QUESTIONS += ['v{0}'.format(i) for i in range(204,210)]
ANALYSIS_QUESTIONS += ['v{0}'.format(i) for i in range(240,243)]
ANALYSIS_QUESTIONS += ['v250']

def initialize_counts(question_id):
    table = db['categories']
    categories = table.find(question_id=question_id)
    category_counts = OrderedDict()

    for category in categories:
        category_counts[category['value']] = 0

    return category_counts


def _query(question_id):
    table = db['codebook']
    question = table.find_one(question_id=question_id)

    result = db.query("""
        select
            countries.value as country, c.value as response
        from
            survey_responses r
        join
            (select * from categories where question_id='{0}') c on r.{0}=c.code
        join
            (select * from categories where question_id='v2a') countries on r.v2a=countries.code
        order by
            country
        ;
    """.format(question_id))

    return question, list(result)


def summarize(question_id):
    question, result = _query(question_id)
    print '{0}: {1}'.format(question_id, question['label'])

    counts = OrderedDict()

    for row in result:
        if not row['country'] in counts.keys():
            counts[row['country']] = initialize_counts(question_id)

        counts[row["country"]][row["response"]] += 1

    output = []
    for country, values in counts.items():
        output_row = OrderedDict((('country', country),))
        total = 0
        for label, value in values.items():
            total += int(value)

        output_row['total_responses'] = total

        for label, value in values.items():
            output_row[label] = value
            pct_label = '{0} pct'.format(label.encode('ascii', 'ignore').decode('ascii'))
            output_row[pct_label] = float(value) / total

        output.append(output_row)

    dataset.freeze(output, format='csv', filename='output/{0}.csv'.format(question_id))


def _get_counts(result, question_id):
    counts = OrderedDict()
    for row in result:
        if not row['country'] in counts.keys():
            counts[row['country']] = initialize_counts(question_id)
        counts[row["country"]][row["response"]] += 1
    return counts


def process_mentioned(question, result, countries):
    counts = _get_counts(result, question['question_id'])
    key = '{0} {1} (% mentioned)'.format(question['question_id'], question['label'])

    for country, data in countries.items():
        data[key] = None

    total = 0
    for country, results in counts.items():
        for count in results.values():
            total += count

        countries[country][key] = float(results['Mentioned']) / float(total)


def process_agree_3way(question, result, countries):
    counts = _get_counts(result, question['question_id'])
    key = '{0} {1} (% agree)'.format(question['question_id'], question['label'])

    for country, data in countries.items():
        data[key] = None

    total = 0
    for country, results in counts.items():
        for count in results.values():
            total += count

        countries[country][key] = float(results['Agree']) / float(total)


def process_agree_4way(question, result, countries):
    counts = _get_counts(result, question['question_id'])
    key = '{0} {1} (% agree strongly and agree)'.format(question['question_id'], question['label'])

    for country, data in countries.items():
        data[key] = None

    total = 0
    for country, results in counts.items():
        for count in results.values():
            total += count

        countries[country][key] = (float(results['Agree']) + float(results['Agree strongly'])) / float(total)


def process_likert(question, result, countries):
    counts = _get_counts(result, question['question_id'])
    key = '{0} {1} (% favorable [#5-#10])'.format(question['question_id'], question['label'])

    for country, data in countries.items():
        data[key] = None

    total = 0
    for country, results in counts.items():
        for count in results.values():
            total += count

        favorable = sum(results.values()[5:10])

        countries[country][key] = float(favorable) / float(total)


def compressed_summarize():
    table = db['categories']
    country_result = list(table.find(question_id='v2a'))
    countries = OrderedDict()
    for row in country_result:
        countries[row['value']] = OrderedDict((('country', row['value']),))

    for question_id in ANALYSIS_QUESTIONS:
        question, result = _query(question_id)

        if question['question_type'] == 'mentioned':
            process_mentioned(question, result, countries)

        if question['question_type'] == 'agree_3way':
            process_agree_3way(question, result, countries)

        if question['question_type'] == 'agree_4way':
            process_agree_4way(question, result, countries)

        if question['question_type'] == 'likert':
            process_likert(question, result, countries)

    dataset.freeze(countries.values(), format='csv', filename='output/summary.csv')


if __name__ == '__main__':
    compressed_summarize()

    for question_id in ANALYSIS_QUESTIONS:
        summarize(question_id)

