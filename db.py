# -*- coding: utf-8 -*-

import dataset
from collections import OrderedDict

POSTGRES_URL = 'postgresql:///worldvalues'
db = dataset.connect(POSTGRES_URL)


def initialize_counts(question_id):
    """
    Initialize counts for summary
    """
    table = db['categories']
    categories = table.find(question_id=question_id)
    category_counts = OrderedDict()

    for category in categories:
        category_counts[category['value']] = 0

    return category_counts


def query(question_id):
    """
    Query for raw results from a question ID
    """
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


def get_country_list():
    """
    Return list of countries
    """
    countries = []
    table = db['categories']
    country_result = list(table.find(question_id='v2a', order_by='value'))
    for row in country_result:
        countries.append(row['value'])

    return countries
