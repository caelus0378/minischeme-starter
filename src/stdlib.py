"""内置过程：spec §5 的全部标准函数。

每个内置过程接收"已求值"的参数列表（args），返回一个值。
"""

import sys

from datatypes import (
    Symbol, Pair, NilType, NIL, BuiltinProcedure, Procedure,
    truthy, is_number, is_proper_list, SchemeError,
)
from printer import display_string


# ---- 通用辅助 -----------------------------------------------------------

def _trunc_div(a, b):
    """整数商，向零截断（与 Python 的 // 向下取整不同）。"""
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def _equal(a, b):
    """equal?：结构相等（逐层比较）。"""
    if is_number(a) and is_number(b):
        return a == b
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a is b
    if type(a) is not type(b):
        return False
    if isinstance(a, Symbol):
        return a.name == b.name
    if isinstance(a, str):
        return a == b
    if isinstance(a, Pair):
        return _equal(a.car, b.car) and _equal(a.cdr, b.cdr)
    if isinstance(a, NilType):
        return True
    return a == b


def _eq(a, b):
    """eq?：符号/数字/布尔按值，复合数据按同一性。"""
    if is_number(a) or is_number(b):
        return is_number(a) and is_number(b) and a == b
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a is b
    if isinstance(a, Symbol) and isinstance(b, Symbol):
        return a.name == b.name
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    if isinstance(a, NilType) and isinstance(b, NilType):
        return True
    return a is b


def _compare(a, b):
    """返回 -1 / 0 / 1；符号按名字比较，数字按数值比较。"""
    ka = a.name if isinstance(a, Symbol) else a
    kb = b.name if isinstance(b, Symbol) else b
    return (ka > kb) - (ka < kb)


def _chain(args, pred):
    """链式比较：相邻两两都成立才为真。"""
    for i in range(len(args) - 1):
        if not pred(args[i], args[i + 1]):
            return False
    return True


# ---- 算术 ---------------------------------------------------------------

def _add(args):
    return sum(args)


def _sub(args):
    if len(args) == 1:
        return -args[0]
    result = args[0]
    for a in args[1:]:
        result -= a
    return result


def _mul(args):
    result = 1
    for a in args:
        result *= a
    return result


def _div(args):
    if len(args) == 1:
        return 1.0 / args[0]  # 单参数求倒数，结果为浮点
    result = args[0]
    for a in args[1:]:
        result = _trunc_div(result, a)
    return result


def _modulo(args):
    return args[0] % args[1]


def _quotient(args):
    return _trunc_div(args[0], args[1])


def _expt(args):
    return args[0] ** args[1]


def _abs(args):
    return abs(args[0])


# ---- 比较 ---------------------------------------------------------------

def _num_equal(args):
    return _chain(args, lambda a, b: _compare(a, b) == 0)


def _lt(args):
    return _chain(args, lambda a, b: _compare(a, b) < 0)


def _gt(args):
    return _chain(args, lambda a, b: _compare(a, b) > 0)


def _le(args):
    return _chain(args, lambda a, b: _compare(a, b) <= 0)


def _ge(args):
    return _chain(args, lambda a, b: _compare(a, b) >= 0)


def _not(args):
    return not truthy(args[0])


# ---- 列表 ---------------------------------------------------------------

def _cons(args):
    return Pair(args[0], args[1])


def _car(args):
    p = args[0]
    if not isinstance(p, Pair):
        raise SchemeError("car: not a pair")
    return p.car


def _cdr(args):
    p = args[0]
    if not isinstance(p, Pair):
        raise SchemeError("cdr: not a pair")
    return p.cdr


def _list(args):
    result = NIL
    for a in reversed(args):
        result = Pair(a, result)
    return result


def _length(args):
    n = 0
    p = args[0]
    while isinstance(p, Pair):
        n += 1
        p = p.cdr
    return n


def _append(args):
    if not args:
        return NIL
    result = args[-1]
    for lst in reversed(args[:-1]):
        result = _append_two(lst, result)
    return result


def _append_two(a, b):
    """把 b 接到 a 的副本末尾，返回新列表。"""
    if not isinstance(a, Pair):
        return b
    head = Pair(a.car, NIL)
    tail = head
    a = a.cdr
    while isinstance(a, Pair):
        tail.cdr = Pair(a.car, NIL)
        tail = tail.cdr
        a = a.cdr
    tail.cdr = b
    return head


# ---- 谓词 ---------------------------------------------------------------

def _null_q(args):
    return isinstance(args[0], NilType)


def _pair_q(args):
    return isinstance(args[0], Pair)


def _list_q(args):
    return is_proper_list(args[0])


def _number_q(args):
    return is_number(args[0])


def _boolean_q(args):
    return isinstance(args[0], bool)


def _symbol_q(args):
    return isinstance(args[0], Symbol)


def _string_q(args):
    return isinstance(args[0], str)


def _procedure_q(args):
    return isinstance(args[0], (BuiltinProcedure, Procedure))


def _zero_q(args):
    return args[0] == 0


def _even_q(args):
    return args[0] % 2 == 0


def _odd_q(args):
    return args[0] % 2 == 1


def _eq_q(args):
    return _eq(args[0], args[1])


def _equal_q(args):
    return _equal(args[0], args[1])


# ---- 输出 ---------------------------------------------------------------

def _display(args):
    sys.stdout.write(display_string(args[0]))
    return None


def _newline(args):
    sys.stdout.write('\n')
    return None


_BUILTINS = {
    '+': _add, '-': _sub, '*': _mul, '/': _div,
    'modulo': _modulo, 'quotient': _quotient, 'expt': _expt, 'abs': _abs,
    '=': _num_equal, '<': _lt, '>': _gt, '<=': _le, '>=': _ge,
    'not': _not,
    'cons': _cons, 'car': _car, 'cdr': _cdr, 'list': _list,
    'length': _length, 'append': _append,
    'null?': _null_q, 'pair?': _pair_q, 'list?': _list_q,
    'number?': _number_q, 'boolean?': _boolean_q, 'symbol?': _symbol_q,
    'string?': _string_q, 'procedure?': _procedure_q,
    'zero?': _zero_q, 'even?': _even_q, 'odd?': _odd_q,
    'eq?': _eq_q, 'equal?': _equal_q,
    'display': _display, 'newline': _newline,
}


def install_builtins(env):
    """把全部内置过程装进环境。"""
    for name, func in _BUILTINS.items():
        env.define(name, BuiltinProcedure(name, func))
