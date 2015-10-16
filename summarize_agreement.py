#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dataset

from db import query, initialize_counts, get_country_list
from collections import OrderedDict


ANALYSIS_QUESTIONS = ['v52', 'v45', 'v51']
ANALYSIS_COUNTRIES = ['India', 'Pakistan', 'Nigeria', 'China', 'Brazil', 'United States']


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

    for country, results in counts.items():
        if country not in countries.keys():
            continue

        total = 0

        for count in results.values():
            total += count

        countries[country][key] = float(results['Mentioned']) / float(total)


def process_agree_3way(question, result, countries):
    counts = _get_counts(result, question['question_id'])
    key = '{0} {1} (% agree)'.format(question['question_id'], question['label'])

    for country, data in countries.items():
        data[key] = None

    for country, results in counts.items():
        if country not in countries.keys():
            continue

        total = 0

        for count in results.values():
            total += count

        countries[country][key] = float(results['Agree']) / float(total)


def process_agree_4way(question, result, countries):
    counts = _get_counts(result, question['question_id'])
    key = '{0} {1} (% agree strongly and agree)'.format(question['question_id'], question['label'])

    for country, data in countries.items():
        data[key] = None

    for country, results in counts.items():
        if country not in countries.keys():
            continue

        total = 0

        for count in results.values():
            total += count

        countries[country][key] = (float(results['Agree']) + float(results['Agree strongly'])) / float(total)


def process_likert(question, result, countries):
    counts = _get_counts(result, question['question_id'])
    key = '{0} {1} (% favorable [#5-#10])'.format(question['question_id'], question['label'])

    for country, data in countries.items():
        data[key] = None

    for country, results in counts.items():
        if country not in countries.keys():
            continue

        total = 0

        for count in results.values():
            total += count

        favorable = sum(results.values()[5:10])

        countries[country][key] = float(favorable) / float(total)


def summarize_agreement():
    """
    Summarize agreement levels
    """
    country_list = get_country_list()
    countries = OrderedDict()
    for country in country_list:
        if country in ANALYSIS_COUNTRIES:
            countries[country] = OrderedDict((('country', country),))

    for question_id in ANALYSIS_QUESTIONS:
        question, result = query(question_id)

        if question['question_type'] == 'mentioned':
            process_mentioned(question, result, countries)

        if question['question_type'] == 'agree_3way':
            process_agree_3way(question, result, countries)

        if question['question_type'] == 'agree_4way':
            process_agree_4way(question, result, countries)

        if question['question_type'] == 'likert':
            process_likert(question, result, countries)

    dataset.freeze(countries.values(), format='csv', filename='output/agreement_summary.csv')


if __name__ == '__main__':
    summarize_agreement()
