import collections

Filter = collections.namedtuple('Filter', ['regex', 'fn'])
class FnMapping:

    def filter_fn(fn, *args):
        def filter(v):
            return fn(*args, v)
        return filter

    def gt(replacement, upper_bound, val):
        if val > upper_bound:
            return replacement
        else:
            return val

    def lt(replacement, lower_bound, val):
        if val < lower_bound:
            return replacement
        else:
            return val

    def gte(replacement, upper_bound, val):
        if val >= upper_bound:
            return replacement
        else:
            return val

    def lte(replacement, lower_bound, val):
        if val <= lower_bound:
            return replacement
        else:
            return val

    def equals(replacement, equals_val, val):
        if val == equals_val:
            return replacement
        else:
            return val
