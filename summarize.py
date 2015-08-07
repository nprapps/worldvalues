#!/usr/bin/env python

from collections import defaultdict, OrderedDict
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

def summarize(question_id):
    table = db['codebook']
    question = table.find_one(question_id=question_id)
    print '{0}: {1}'.format(question_id, question['label'])

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
    for question_id in ANALYSIS_QUESTIONS:
        summarize(question_id)
