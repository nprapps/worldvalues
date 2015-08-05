#!/usr/bin/env python

from collections import defaultdict, OrderedDict
import dataset

POSTGRES_URL = 'postgresql:///worldvalues'
db = dataset.connect(POSTGRES_URL)

def initialize_counts(question_id):
    table = db['categories']
    categories = table.find(question_id=question_id)
    category_counts = OrderedDict()

    for category in categories:
        category_counts[category['value']] = 0

    return category_counts

def summarize(question_id):
    result= db.query("""
        select 
            countries.value as country, c.value as response
        from
            survey_responses r
        join
            (select * from categories where question_id='{0}') c on r.{0}=c.code
        join
            (select * from categories where question_id='v2a') countries on r.v2a=countries.code    
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
        for label, value in values.items():
            output_row[label] = float(value) / total

        output.append(output_row)

    dataset.freeze(output, format='csv', filename='output/{0}.csv'.format(question_id))

if __name__ == '__main__':
    summarize('v54')
