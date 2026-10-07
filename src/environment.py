"""环境：变量到值的绑定表，带指向外层环境的指针。

查找名字时沿着 parent 链向上走，这就是词法作用域的基础。
"""

from datatypes import SchemeError


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.bindings = {}

    def define(self, name, value):
        """在当前环境绑定（或覆盖）一个名字。"""
        self.bindings[name] = value

    def lookup(self, name):
        """从当前环境向外层逐级查找名字。"""
        env = self
        while env is not None:
            if name in env.bindings:
                return env.bindings[name]
            env = env.parent
        raise SchemeError("undefined symbol: " + name)
