"""语法分析：把 token 列表变成嵌套的表达式结构。

表达式用 Python 列表表示函数调用/特殊形式，原子（数字/布尔/字符串/符号）
原样保留；引用简写 'x 展开成 (quote x)。
"""

from datatypes import Symbol


def parse(tokens):
    """返回顶层表达式列表。"""
    exprs = []
    i = 0
    while i < len(tokens):
        expr, i = _parse_one(tokens, i)
        exprs.append(expr)
    return exprs


def _parse_one(tokens, i):
    tok = tokens[i]
    if tok == '(':
        lst = []
        i += 1
        while i < len(tokens) and tokens[i] != ')':
            sub, i = _parse_one(tokens, i)
            lst.append(sub)
        return lst, i + 1  # 跳过 ')'；i+1 在越界时不成立，但合法输入必有闭括号
    if tok == "'":
        quoted, i = _parse_one(tokens, i + 1)
        return [Symbol('quote'), quoted], i
    return tok, i + 1
