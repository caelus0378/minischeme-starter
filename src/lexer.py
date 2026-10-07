"""词法分析：把程序文本切成 token 列表。

每个 token 是以下之一：
  '(' ')' "'" —— 结构符号
  数字（int/float）、布尔（True/False）、字符串（str）—— 字面量
  Symbol —— 符号（名字）
"""

import re

from datatypes import Symbol

_NUMBER_RE = re.compile(r'^-?\d+(\.\d+)?$')
_DELIMS = set(' \t\r\n();"\'')  # 符号或数字的结束边界


def tokenize(source):
    tokens = []
    i = 0
    n = len(source)
    while i < n:
        c = source[i]
        if c in ' \t\r\n':
            i += 1
        elif c == ';':
            # 注释：忽略到行尾
            while i < n and source[i] != '\n':
                i += 1
        elif c in '()':
            tokens.append(c)
            i += 1
        elif c == "'":
            tokens.append(c)
            i += 1
        elif c == '"':
            raw, i = _read_string(source, i)
            tokens.append(_decode_string(raw))
        else:
            j = i
            while j < n and source[j] not in _DELIMS:
                j += 1
            tok = source[i:j]
            if tok == '#t':
                tokens.append(True)
            elif tok == '#f':
                tokens.append(False)
            elif _NUMBER_RE.match(tok):
                tokens.append(float(tok) if '.' in tok else int(tok))
            else:
                tokens.append(Symbol(tok))
            i = j
    return tokens


def _read_string(source, i):
    """从开引号 i 读到闭引号，返回 (原始内容, 闭引号之后的位置)。

    反斜杠后的字符（含 \"）原样收进 raw 并由 _decode_string 还原，
    因此转义的引号不会提前结束字符串。
    """
    j = i + 1
    raw = []
    n = len(source)
    while j < n and source[j] != '"':
        c = source[j]
        if c == '\\' and j + 1 < n:
            raw.append(c)
            raw.append(source[j + 1])
            j += 2
        else:
            raw.append(c)
            j += 1
    return ''.join(raw), j + 1


def _decode_string(raw):
    """把转义序列（\\n \\t \\" \\\\）还原成真实字符。"""
    out = []
    i = 0
    n = len(raw)
    while i < n:
        c = raw[i]
        if c == '\\' and i + 1 < n:
            nxt = raw[i + 1]
            if nxt == 'n':
                out.append('\n')
            elif nxt == 't':
                out.append('\t')
            elif nxt == '"':
                out.append('"')
            elif nxt == '\\':
                out.append('\\')
            else:
                out.append(c)
                out.append(nxt)
            i += 2
        else:
            out.append(c)
            i += 1
    return ''.join(out)
