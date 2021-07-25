"""
Local collection of past prediction inputs for specific regions.
Used as a guidance example for users.

Each location comes with the following information:
* Input specifications, in form of json string
* Name
"""

from collections import defaultdict

loc = defaultdict()
name = defaultdict()

loc['hcmc'] = '''
{
    "N": 9000000,
    "n_r0": 5,
    "r0": 4.1,
    "delta_r0": [
        1.3,
        1.1,
        1,
        1,
        0.9
    ],
    "pcont": [
        0.1,
        0.2,
        0.35,
        0.5,
        0.65
    ],
    "day": [
        8,
        21,
        29,
        37,
        70
    ],
    "date": "2021-05-01",
    "hcap": 50000,
    "hqar": 50000,
    "tinc": 4.5,
    "tinf": 3,
    "ticu": 11,
    "thsp": 14,
    "tcrt": 7,
    "trec": 14,
    "tqar": 14,
    "tqah": 2,
    "pquar": 0.8,
    "pcross": 0.15,
    "pqhsp": 0.1,
    "pj": 0.12,
    "ph": 0.8,
    "pc": 0.04,
    "pf": 0.22
}
'''
name['hcmc'] = 'Ho Chi Minh City, Vietnam (Moderate Scenario - 5/2021)'

loc['hcmc_worst'] = '''
{
    "N": 9000000,
    "n_r0": 5,
    "r0": 4.1,
    "delta_r0": [
        1.3,
        1.1,
        1,
        0.9,
        0.8
    ],
    "pcont": [
        0.1,
        0.2,
        0.35,
        0.5,
        0.6
    ],
    "day": [
        8,
        21,
        29,
        37,
        70
    ],
    "date": "2021-05-01",
    "hcap": 50000,
    "hqar": 50000,
    "tinc": 4.5,
    "tinf": 3,
    "ticu": 11,
    "thsp": 14,
    "tcrt": 7,
    "trec": 14,
    "tqar": 14,
    "tqah": 2,
    "pquar": 0.8,
    "pcross": 0.15,
    "pqhsp": 0.1,
    "pj": 0.12,
    "ph": 0.8,
    "pc": 0.04,
    "pf": 0.22
}
'''
name['hcmc_worst'] = 'Ho Chi Minh City, Vietnam (Worst Scenario - 5/2021)'

loc['hcmc_best'] = '''
{
    "N": 9000000,
    "n_r0": 5,
    "r0": 4.1,
    "delta_r0": [
        1.3,
        1.1,
        1,
        1,
        1
    ],
    "pcont": [
        0.1,
        0.2,
        0.35,
        0.53,
        0.68
    ],
    "day": [
        8,
        21,
        29,
        37,
        70
    ],
    "date": "2021-05-01",
    "hcap": 50000,
    "hqar": 50000,
    "tinc": 4.5,
    "tinf": 3,
    "ticu": 11,
    "thsp": 14,
    "tcrt": 7,
    "trec": 14,
    "tqar": 14,
    "tqah": 2,
    "pquar": 0.8,
    "pcross": 0.15,
    "pqhsp": 0.1,
    "pj": 0.12,
    "ph": 0.8,
    "pc": 0.04,
    "pf": 0.22
}
'''
name['hcmc_best'] = 'Ho Chi Minh City, Vietnam (Best Scenario - 5/2021)'

loc['hd'] = '''
{
    "N": 1900000,
    "n_r0": 5,
    "r0": 3.5,
    "delta_r0": [
        1.5,
        1.5,
        1,
        1.5,
        2
    ],
    "pcont": [
        0.5,
        0.6,
        0.8,
        0.6,
        0.2
    ],
    "day": [
        21,
        35,
        43,
        54,
        83
    ],
    "date": "2021-01-07",
    "ndate": 150,
    "hcap": 1000,
    "hqar": 10000,
    "tinc": 5.2,
    "tinf": 3.0,
    "ticu": 11,
    "thsp": 21,
    "tcrt": 7,
    "trec": 14,
    "tqar": 14,
    "tqah": 2,
    "pquar": 0.75,
    "pcross": 0.01,
    "pqhsp": 0.1,
    "pj": 0.12,
    "ph": 0.75,
    "pc": 0.04,
    "pf": 0
}
'''
name['hd'] = 'Hai Duong, Vietnam (1/2021-3/2021)'

loc['dn'] = '''
{
    "N": 1134000,
    "n_r0": 3,
    "r0": 3.4,
    "delta_r0": [
        0.8,
        1,
        1
    ],
    "pcont": [
        0.2,
        0.75,
        0.5
    ],
    "day": [
        18,
        22,
        65
    ],
    "date": "2021-07-07",
    "ndate": 100,
    "hcap": 100000,
    "hqar": 10000,
    "tinc": 5.2,
    "tinf": 2.9,
    "ticu": 11,
    "thsp": 21,
    "tcrt": 7,
    "trec": 14,
    "tqar": 14,
    "tqah": 2,
    "pquar": 0.66,
    "pcross": 0.01,
    "pqhsp": 0.1,
    "pj": 0.12,
    "ph": 0.66,
    "pc": 0.2,
    "pf": 0.25
}
'''
name['dn'] = 'Da Nang, Vietnam (7/2020-9/2020)'