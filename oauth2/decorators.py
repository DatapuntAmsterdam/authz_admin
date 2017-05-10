""" Some decorators used throughout the code.
"""

from functools import wraps, update_wrapper


def memoized(f):
    """
    Decorator that memoizes the return value of a function.

    :param f: the function to decorate. Gets called no more than once.

    :return: whatever `f` returns.

    """
    called = False
    value = None

    @wraps(f)
    def x():
        nonlocal called, value
        if not called:
            value = f()
            called = True
        return value

    return x


class reify(object):
    """ Copied from `Pyramid <https://trypyramid.com/>`_

    Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val
