from typing import List
import string
import os


class Apply:
    def __init__(self, first, second=None):
        self.first = first
        self.second = second  # None 表示这是个变量

    def py(self):
        first, second = self.first, self.second
        res = f"{first.py()}" if type(first) is not str else f"{first}"
        while second is not None:
            first = second.first
            if type(first) is str:
                res = (
                    f"({res})({first})" if len(res) > 1 else f"{res}({first})"
                )
            else:
                res = (
                    f"({res})({first.py()})"
                    if len(res) > 1
                    else f"{res}({first.py()})"
                )

            second = second.second
        return res

    def __str__(self) -> str:
        first, second = self.first, self.second
        res = (
            f"({first})"
            if isinstance(first, Lambda) and second
            else f"{first}"
        )
        while second is not None:
            first = second.first if hasattr(second, "first") else second
            res = f"{res}{first}" if type(first) is str else f"{res}({first})"
            second = second.second if hasattr(second, "second") else None
        return res


class Lambda:
    def __init__(self, arg, body):
        self.arg = arg
        self.body = body

    def py(self):
        return f"lambda {self.arg}: {self.body.py()}"

    def __str__(self):
        exp = self
        res = "λ"
        while isinstance(exp.body, Lambda):
            res += exp.arg
            exp = exp.body
        res += f"{exp.arg}.{exp.body}"
        return res


def tree_equal(ast1, ast2):
    if isinstance(ast1, Apply) and isinstance(ast2, Apply):
        return tree_equal(ast1.first, ast2.first) and tree_equal(
            ast1.second, ast2.second
        )
    if isinstance(ast1, Lambda) and isinstance(ast2, Lambda):
        return tree_equal(ast1.body, ast2.body)
    if type(ast1) is str and type(ast2) is str:
        return ast1 == ast2
    return False


class LLLparser:
    def __init__(self, s):
        self.s = "".join(s.split())  # delete spacees
        self.i = 0

    def parse_apply(self):
        if self.i == len(self.s) or self.s[self.i] == ")":
            return None
        if self.s[self.i] == "(":
            self.i += 1
            first = self.parse()
            assert self.s[self.i] == ")", "parentheses not match"
            self.i += 1
        else:
            first = self.s[self.i]
            self.i += 1
        return Apply(first, self.parse_apply())

    def parse_lambda(self):
        if self.s[self.i] == ".":
            self.i += 1
            return self.parse()
        var = self.s[self.i]
        self.i += 1
        return Lambda(var, self.parse_lambda())

    def parse(self):
        if self.s[self.i] == "(" and self.s[self.i + 1] in "Lλ":
            self.i += 2
            lmb = self.parse_lambda()
            assert self.s[self.i] == ")", "parentheses not match"
            self.i += 1
            return Apply(lmb, self.parse_apply())

        if self.s[self.i] in "Lλ":
            self.i += 1
            return self.parse_lambda()
        return self.parse_apply()


def read_and_parse(path: str):
    """
    expressions are split by double "\n"
    """
    with open(path) as f:
        string = f.read()

    expressions_str = string.split("\n")
    subst_map = {}
    for exp in expressions_str:
        if exp.strip() == "" or exp.startswith(";") or exp.startswith("#"):
            continue
        if "=" in exp:
            key, value = exp.split("=")

            parser = LLLparser(preprocess(value.strip(), subst_map))
            ast = parser.parse()

            subst_map[key.strip()] = str(
                evaluate(ast) if isinstance(ast, Apply) else ast
            )

            continue
        print(exp, end="-> ")
        exp_ = preprocess(exp.strip(), subst_map)
        ast = LLLparser(exp_).parse()

        if numerical(exp):
            res = evaluate(ast)
            print(f"{decode(res)}: {res} ")
        else:
            res = evaluate(ast)
            print(res)


def numerical(exp):
    return any(
        x in exp
        for x in ["FACT", "PRED", "ADD", "MUL", "ACC", "EXP", "ISZERO"]
    )


class VariableGenerator:
    def __init__(self, vars=set()):
        self.vars = vars
        from itertools import product, chain

        base = string.ascii_lowercase
        self.hub = chain(base, product(base, range(100)))

    def __call__(self):
        for ele in self.hub:
            if type(ele) is tuple:
                ele = ele[0] + str(ele[1])
            if ele not in self.vars:
                self.vars.add(ele)
                return ele
        raise ValueError("no more variable")


def get_variables(exp):
    if isinstance(exp, Apply):
        return get_variables(exp.first) | get_variables(exp.second)
    if isinstance(exp, Lambda):
        return {exp.arg} | get_variables(exp.body)
    if type(exp) is str:
        return {exp}
    return set()


def preprocess(exp, subst_map):
    import re

    subst_lst = list(subst_map.items())
    subst_lst.sort(key=lambda x: (len(x[0]), x[0]), reverse=True)
    for key, value in subst_lst:
        if not value.startswith("("):
            value = f"({value})"
        exp = re.sub(key, value, exp)
    return exp


def print_tree(ast, indent=0):
    if isinstance(ast, Apply):
        print(" " * indent + "Apply:")
        print_tree(ast.first, indent + 2)
        print_tree(ast.second, indent + 2)
    if isinstance(ast, Lambda):
        print(" " * indent + "Lambda:")
        print_tree(ast.arg, indent + 2)
        print_tree(ast.body, indent + 2)
    if type(ast) is str:
        print(" " * indent + ast)


def alpha_conv(exp, var, generator):
    """
    replace all var in exp with a new variable generated by generator
    """
    if not isinstance(exp, Lambda) or var != exp.arg:
        return exp

    new_var = generator()

    def _alpha(exp):
        if isinstance(exp, Apply):
            return Apply(_alpha(exp.first), _alpha(exp.second))
        if isinstance(exp, Lambda):
            if exp.arg == var:
                return exp
            return Lambda(exp.arg, _alpha(exp.body))
        if exp == var:
            return new_var
        return exp

    return Lambda(new_var, _alpha(exp.body))


def beta_reduce(exp, env={}, generator=None):
    if type(exp) is str:
        return env.get(exp, exp)

    if isinstance(exp, Lambda):
        if env:
            key = list(env.keys())[0]
            all_variables = get_variables(env[key])
            if exp.arg in all_variables and key in get_variables(exp.body):
                exp = alpha_conv(exp, exp.arg, generator)

            env = {key: value for key, value in env.items() if exp.arg != key}
        return Lambda(exp.arg, beta_reduce(exp.body, env, generator))

    if isinstance(exp, Apply):
        if env != {}:
            return Apply(
                beta_reduce(exp.first, env, generator),
                beta_reduce(exp.second, env, generator),
            )

        if isinstance(exp.first, Lambda):
            if exp.second is None:
                return exp.first

            lam = exp.first

            value, remain = exp.second, None

            if isinstance(exp.second, Apply):
                value, remain = exp.second.first, exp.second.second

            env = {lam.arg: value}  # only one
            return Apply(beta_reduce(lam.body, env, generator), remain)
        return reduce_list(exp, env, generator)
    return exp


def reduce_list(exp, env, generator):
    return (
        Apply(
            beta_reduce(exp.first, env, generator),
            reduce_list(exp.second, env, generator),
        )
        if hasattr(exp, "second")
        else beta_reduce(exp, env, generator)
    )


def evaluate(ast, max_step=2000):
    for _ in range(max_step):
        generator = VariableGenerator(get_variables(ast))
        ast_after = beta_reduce(ast, {}, generator)
        if tree_equal(ast, ast_after):
            return ast
        ast = ast_after

    return ast


def decode(lam: Lambda):
    def inc(x):
        return x + 1

    exp = eval(lam.py())
    try:
        return exp(1)(0)
    except:
        return exp(inc)(0)


def test_evaluate_file():
    path = os.path.abspath(__file__)
    file_name = path.split("/")[-1].split(".")[0]
    test_file = f"tests/{file_name}.lambda"
    read_and_parse(test_file)


if __name__ == "__main__":
    test_evaluate_file()
