"""求值器：表达式 -> 值（解释器的心脏）。

evaluate 与 apply 互相递归：
  evaluate 遇到函数调用就去 apply，
  apply 执行用户函数体又调回 evaluate。
"""

from datatypes import (
    Symbol, Pair, Procedure, BuiltinProcedure,
    truthy, SchemeError, list_to_pair,
)
from environment import Environment


def evaluate(expr, env):
    # 自求值：数字、布尔、字符串
    if isinstance(expr, (int, float, bool, str)):
        return expr
    # 变量引用：去环境查值
    if isinstance(expr, Symbol):
        return env.lookup(expr.name)
    # 括号表达式：特殊形式或函数调用
    if isinstance(expr, list):
        if not expr:
            return list_to_pair([])  # 空的 () 视为空表
        head = expr[0]
        if isinstance(head, Symbol):
            name = head.name
            if name == 'quote':
                return list_to_pair(expr[1])
            if name == 'if':
                return _eval_if(expr[1:], env)
            if name == 'cond':
                return _eval_cond(expr[1:], env)
            if name == 'and':
                return _eval_and(expr[1:], env)
            if name == 'or':
                return _eval_or(expr[1:], env)
            if name == 'define':
                return _eval_define(expr[1:], env)
            if name == 'lambda':
                return _eval_lambda(expr[1:], env)
            if name == 'let':
                return _eval_let(expr[1], expr[2:], env)
            if name == 'begin':
                return _eval_sequence(expr[1:], env)
        # 普通函数调用：先求值操作符和全部实参，再交给 apply
        proc = evaluate(head, env)
        args = [evaluate(a, env) for a in expr[1:]]
        return apply_proc(proc, args)
    raise SchemeError("cannot evaluate: " + repr(expr))


def apply_proc(proc, args):
    if isinstance(proc, BuiltinProcedure):
        return proc.func(args)
    if isinstance(proc, Procedure):
        # 新建一层环境：实参绑到形参，外层指向函数"定义时"的环境
        new_env = Environment(proc.env)
        for param, arg in zip(proc.params, args):
            new_env.define(param.name, arg)
        return _eval_sequence(proc.body, new_env)
    raise SchemeError("not a procedure: " + repr(proc))


# ---- 特殊形式 -----------------------------------------------------------

def _eval_if(args, env):
    if truthy(evaluate(args[0], env)):
        return evaluate(args[1], env)
    if len(args) > 2:
        return evaluate(args[2], env)
    return None  # 无假分支时返回 None（不打印）


def _eval_cond(clauses, env):
    for clause in clauses:
        if not clause:
            continue
        test = clause[0]
        body = clause[1:]
        if isinstance(test, Symbol) and test.name == 'else':
            return _eval_sequence(body, env) if body else True
        result = evaluate(test, env)
        if truthy(result):
            return _eval_sequence(body, env) if body else result
    return None


def _eval_and(exprs, env):
    value = True
    for e in exprs:
        value = evaluate(e, env)
        if not truthy(value):
            return False  # 短路
    return value


def _eval_or(exprs, env):
    for e in exprs:
        value = evaluate(e, env)
        if truthy(value):
            return value  # 短路
    return False


def _eval_define(args, env):
    target = args[0]
    if isinstance(target, Symbol):
        # (define 名 表达式)：先求值右侧，再绑定
        value = evaluate(args[1], env)
        env.define(target.name, value)
        return target
    if isinstance(target, list):
        # (define (函数名 参数...) 体...) —— 函数定义简写
        name = target[0]
        proc = Procedure(target[1:], args[1:], env)
        env.define(name.name, proc)
        return name
    raise SchemeError("bad define")


def _eval_lambda(args, env):
    return Procedure(args[0], args[1:], env)


def _eval_let(bindings, body, env):
    # 并行绑定：所有绑定表达式先在外层环境求值完，互不可见
    names = [b[0].name for b in bindings]
    values = [evaluate(b[1], env) for b in bindings]
    new_env = Environment(env)
    for name, value in zip(names, values):
        new_env.define(name, value)
    return _eval_sequence(body, new_env)


def _eval_sequence(exprs, env):
    result = None
    for e in exprs:
        result = evaluate(e, env)
    return result
