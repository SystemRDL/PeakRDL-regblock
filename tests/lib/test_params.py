from itertools import product

def get_permutations(spec):
    param_list = []
    for v in product(*spec.values()):
        param_list.append(dict(zip(spec, v)))
    return param_list
