#!/usr/bin/env python

from collections import defaultdict
import dataset


POSTGRES_URL = 'postgresql:///worldvalues'
db = dataset.connect(POSTGRES_URL)

def default_factory():
    return defaultdict(int)

def summarize_v45():
    result= db.query("""
        select 
            countries.value as country, c.value as response
        from
            survey_responses r 
        join 
            (select * from categories where question_id='v45') c on r.v45=c.code
        join
            (select * from categories where question_id='v2a') countries on r.v2a=countries.code    
        ;
    """)

    counts= defaultdict(default_factory)
    for row in result:
        counts[row["country"]][row["response"]] +=1
    print counts
    

if __name__ == '__main__':
    summarize_v45()
