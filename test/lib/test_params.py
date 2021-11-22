from itertools import product

from .cpuifs.apb3 import APB3, FlatAPB3


all_cpuif = [
    APB3(),
    FlatAPB3(),
]

def get_permutations(spec):
    param_list = []
    for v in product(*spec.values()):
        param_list.append(dict(zip(spec, v)))
    return param_list

#-------------------------------------------------------------------------------
# TODO: this wont scale well. Create groups of permutatuions. not necessary to permute everything all the time.
TEST_PARAMS = get_permutations({
    "cpuif": all_cpuif,
    "retime_read_fanin": [True, False],
    "retime_read_response": [True, False],
})
