"""
Providing iterator functions that are not in all version of Python we support.
Where possible, we try to use the system-native version and only fall back to
these implementations if necessary.
"""

import itertools

__all__ = [
    'all',
    'any',
    'is_iterable',
    'product',
]

# Fallback for Python 2.4, Python 2.5
def _product(*args, **kwds):
    """
    Taken from http://docs.python.org/library/itertools.html#itertools.product
    """
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)
product = getattr(itertools, 'product', _product)

def is_iterable(x):
    "A implementation independent way of checking for iterables"
    try:
        iter(x)
    except TypeError:
        return False
    else:
        return True

def _all(iterable):
    """
    Taken from http://docs.python.org/library/functions.html#all
    """
    for item in iterable:
        if not item:
            return False
    return True
all = getattr(__builtins__, "all", _all)

def _any(iterable):
    """
    Taken from http://docs.python.org/library/functions.html#any
    """
    for element in iterable:
        if element:
            return True
    return False
any = getattr(__builtins__, "any", _any)
