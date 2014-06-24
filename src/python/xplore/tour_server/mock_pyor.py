import os
import random

_CHANCE = 0.3


def get_path(start, end):
    data_file = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir,
                                             os.pardir, os.pardir, os.pardir,
                                             'data/valid_images.csv'))
    results = []
    with open(data_file, 'r') as images:
        for line in images:
            tokens = line.strip().split(',')
            if random.random() < _CHANCE:
                results.append(tokens[0])
    random.shuffle(results)
    return results
