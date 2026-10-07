"""打印：把值转成文本（spec §8）。

有两种模式：
  write   —— 规范表示（字符串带引号、转义）
  display —— 字符串不带引号、不转义
"""

from datatypes import (
    Symbol, Pair, NilType, Procedure, BuiltinProcedure,
)


def write(value):
    """规范表示，用于顶层结果打印。"""
    return _to_string(value, display=False)


def display_string(value):
    """display 用的表示（字符串原文输出）。"""
    return _to_string(value, display=True)


def _to_string(value, display):
    if isinstance(value, bool):
        return '#t' if value else '#f'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value if display else '"' + _escape(value) + '"'
    if isinstance(value, Symbol):
        return value.name
    if isinstance(value, Pair):
        return _pair_string(value, display)
    if isinstance(value, NilType):
        return '()'
    if isinstance(value, (Procedure, BuiltinProcedure)):
        return '#<procedure>'
    return str(value)


def _pair_string(pair, display):
    """列表打印；遇到不以空表结尾的链则打印点（如 (1 . 2)）。"""
    parts = []
    cur = pair
    while isinstance(cur, Pair):
        parts.append(_to_string(cur.car, display))
        cur = cur.cdr
    if isinstance(cur, NilType):
        return '(' + ' '.join(parts) + ')'
    return '(' + ' '.join(parts) + ' . ' + _to_string(cur, display) + ')'


def _escape(s):
    out = []
    for ch in s:
        if ch == '\\':
            out.append('\\\\')
        elif ch == '"':
            out.append('\\"')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\t':
            out.append('\\t')
        else:
            out.append(ch)
    return ''.join(out)
