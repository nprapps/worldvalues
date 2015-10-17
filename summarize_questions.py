#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dataset
import sys

from collections import OrderedDict
from db import query, initialize_counts


ANALYSIS_QUESTIONS = ['v{0}'.format(i) for i in range(12,23)]
ANALYSIS_QUESTIONS += ['v45', 'v47', 'v48']
ANALYSIS_QUESTIONS += ['v{0}'.format(i) for i in range(50,55)]
ANALYSIS_QUESTIONS += ['v80', 'v123', 'v139', 'v145', 'v147', 'v148', 'v152', 'v168', 'v182', 'v203a']
ANALYSIS_QUESTIONS += ['v{0}'.format(i) for i in range(204,210)]
ANALYSIS_QUESTIONS += ['v{0}'.format(i) for i in range(240,243)]
ANALYSIS_QUESTIONS += ['v250']


def summarize_question(question_id):
    """
    Summarize responses for a given question ID
    """

    question, result = query(question_id)
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

if __name__ == '__main__':
    if len(sys.argv) > 1:
        questions = sys.argv[1:]
    else:
        questions = ANALYSIS_QUESTIONS

    for question_id in questions:
        summarize_question(question_id)
