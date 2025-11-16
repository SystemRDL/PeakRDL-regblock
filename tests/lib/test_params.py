from itertools import product


def get_permutations(spec):
    param_list = []
    for v in product(*spec.values()):
        param_list.append(dict(zip(spec, v)))
    return param_list


def get_permutation_class_name(cls, num: int, params: dict) -> str:
    class_name = cls.__name__

    for val in params.values():
        val_str = str(val)
        if "object at" in val_str:
            val_str = type(val).__name__
        class_name += f"_{val_str}"

    return class_name
