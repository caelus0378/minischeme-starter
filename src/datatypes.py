"""值类型定义。

解释器在"求值"阶段里传递的数据都是"值"：数字、布尔、字符串、符号、
点对（列表）、过程。把它们集中在这一层表示，便于打印器与求值器复用。
"""


class Symbol:
    """符号：表示一个名字（变量名或操作符名），与字符串是两种不同事物。"""
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Pair:
    """点对：由 car 和 cdr 组成，列表就是一层层嵌套的点对链。"""
    __slots__ = ('car', 'cdr')

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr


class NilType:
    """空表 ()：整个语言里只有一个空表实例。"""
    __slots__ = ()

    def __repr__(self):
        return '()'


NIL = NilType()


class Procedure:
    """用户定义的闭包：记录形参、函数体与定义时的环境（词法作用域的关键）。"""
    __slots__ = ('params', 'body', 'env')

    def __init__(self, params, body, env):
        self.params = params   # 形参符号列表
        self.body = body       # 函数体表达式列表
        self.env = env         # 定义处的环境


class BuiltinProcedure:
    """内置过程：直接用一个 Python 函数实现。"""
    __slots__ = ('name', 'func')

    def __init__(self, name, func):
        self.name = name
        self.func = func       # func(args) -> value，args 已全部求值


class SchemeError(Exception):
    """求值过程中的错误。"""


def truthy(x):
    """只有 #f 是假；0、()、"" 都是真。"""
    return x is not False


def is_number(x):
    """是否为数字（布尔不算数字）。"""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_proper_list(x):
    """是否为真列表（以空表结尾的点对链）。"""
    while isinstance(x, Pair):
        x = x.cdr
    return isinstance(x, NilType)


def list_to_pair(data):
    """把 quote 的数据（Python 嵌套列表）转成与 cons 一致的点对链。"""
    if isinstance(data, list):
        result = NIL
        for item in reversed(data):
            result = Pair(list_to_pair(item), result)
        return result
    return data
