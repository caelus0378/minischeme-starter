"""入口：读文件或标准输入，逐条求值顶层表达式并打印结果。

用法：
  python3 src/main.py [file1.scm [file2.scm ...]]
无参数时从标准输入读取；多个文件共享同一个全局环境。
"""

import sys

from lexer import tokenize
from parser import parse
from environment import Environment
from stdlib import install_builtins
from evaluator import evaluate
from printer import write
from datatypes import SchemeError


def global_environment():
    env = Environment()
    install_builtins(env)
    return env


def run(source, env):
    for expr in parse(tokenize(source)):
        result = evaluate(expr, env)
        if result is not None:
            # 每个求值结果独占一行；None（如 display/newline）不打印
            sys.stdout.write(write(result) + '\n')


def main():
    # 递归（fib/sum-to/map 等）可能较深，放宽 Python 的递归上限
    sys.setrecursionlimit(100000)
    try:
        # 让换行符按 \\n 原样写出，避免 Windows 上被转成 \\r\\n
        sys.stdout.reconfigure(newline='\n')
    except Exception:
        pass

    env = global_environment()
    args = sys.argv[1:]
    try:
        if args:
            for path in args:
                with open(path, encoding='utf-8') as f:
                    run(f.read(), env)
        else:
            run(sys.stdin.read(), env)
    except SchemeError as e:
        print("error: " + str(e), file=sys.stderr)
        sys.exit(1)
    sys.stdout.flush()


if __name__ == '__main__':
    main()
