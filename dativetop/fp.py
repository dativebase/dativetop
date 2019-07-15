from collections import namedtuple
import typing


sl_map = map  # standard lib map


Nothing = namedtuple('Nothing', '')

nothing = Nothing()

Maybe = namedtuple(
    'Maybe', (
        'type',
        'value'))

good_maybe = Maybe(type=str, value='dog')
bad_maybe = Maybe(type=str, value=nothing)


def get_len(thing: str) -> int:
    return len(thing)


def add(b: int, a: int) -> int:
    return a + b


def fake(z: int, a: str, m: bool, zz: tuple, aa: float) -> bool:
    return True


def map_over_maybe(func, *maybes):
    # a -> b -> f a -> f b
    # len (str -> int) -> Maybe str -> Maybe int
    # >>> fp.get_len.__annotations__
    # {'thing': <class 'str'>, 'return': <class 'int'>}
    maybe_types = [m.type for m in maybes]
    maybe_values = [m.value for m in maybes]
    print('maybe values')
    print(maybe_values)
    try:
        *func_input_types, func_ret_type = typing.get_type_hints(func).values()
    except Exception as exc:
        raise TypeError(
            f'Function {func} has no type hints. It cannot be mapped over a'
            f' maybe.')
    if maybe_types != func_input_types:
        raise TypeError(
            f'Function {func} with type signature {func_input_types} cannot be'
            f' mapped over maybe(s) of type(s) {maybe_types}.')
    try:
        ret_value = func(*maybe_values)
    except Exception as exc:
        ret_value = nothing
    finally:
        return Maybe(type=func_ret_type, value=ret_value)


def map(func, *iterables):
    if isinstance(iterables[0], Maybe):
        return map_over_maybe(func, *iterables)
    return sl_map(func, *iterables)

