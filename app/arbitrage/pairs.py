from itertools import combinations


def generate_exchange_pairs(exchanges):

    return list(combinations(exchanges, 2))