"""
Implementation of the abbreviated Tables and a compiler to translate the high level abbreviated tables 
to the low level transition rules

This script almost reproduces chapter 4 "Abbreviated tables" in the Turing's 1936 paper, 
replacing the human brain with python code to interpret the abbreviated tables

Author: Metaesc
Email: metaescape@foxmail.com
License: MIT License
"""

try:
    from turing_machine.op_extend import Table, TransitionRule, TuringMachine
except:
    from op_extend import Table, TransitionRule, TuringMachine


class SkelotonCompiler(type):
    """
    This is a metaclass to implement the singleton pattern.
    it is also a compiler to translate the high level abbreviated tables which are the instances of AbbreviatedTable
    to the low level transition rules which can be executed by the original Turing Machine
    """

    _instances: dict = {}
    _instances2name: dict = {}
    cnt = 1
    obj2name = {}

    def __call__(cls, *args, **kwargs):
        assert kwargs == {}, "SingletonMeta does not support kwargs"
        key = f"{cls.__name__}{args}"
        if key not in cls._instances:
            # call new to get a pure instance without content (no constructor called)
            instance = cls.__new__(cls, *args, **kwargs)
            # this line should be called before the init to avoid infinite loop
            cls._instances[key] = instance
            cls._instances2name[instance] = key
            # call init to initialize the instance manually
            instance.__init__(*args, **kwargs)
        else:
            print(f"{key} exist, ignore")
        return cls._instances[key]

    @classmethod
    def reset(cls):
        cls._instances = {}
        cls._instances2name = {}
        cls.cnt = 1
        cls.obj2name = {}

    @classmethod
    def get_m_configs(cls):
        return cls._instances

    @classmethod
    def get_objs(cls):
        return cls._instances2name

    @classmethod
    def get_m_config_name(cls, obj):
        return cls.obj2name[obj]

    @classmethod
    def next_m_config_name(cls):
        name = f"q{cls.cnt}"
        cls.cnt += 1
        return name

    @classmethod
    def build_alias_map(cls):
        alias_map = {}
        for abb in cls._instances2name.keys():
            if abb.alias:
                alias_map[abb.alias] = abb
        return alias_map

    @classmethod
    def compile(cls):
        """
        generate machine code
        - build the alias map, then replace the object with the final alias obj(the public obj of the abbreviated table)
        - replace the state obj to a string (public name of the abbreviated table)
        - generate the low level transition rules
        """
        table = Table()
        rules = []

        alias_map = cls.build_alias_map()

        for abb in cls._instances2name.keys():

            for symbol, operations, next_m_config in abb.transitions:
                if abb in alias_map:
                    abb = cls.get_root(alias_map, abb)

                if next_m_config in alias_map:
                    next_m_config = cls.get_root(alias_map, next_m_config)
                rules.append([abb, symbol, operations, next_m_config])

        # replace the python object with the m-config name

        for abb, symbol, operations, next_m_config in rules:
            if type(abb) != str:
                if abb in cls.obj2name:
                    abb = cls.obj2name[abb]
                else:
                    cls.obj2name[abb] = cls.next_m_config_name()
                    abb = cls.obj2name[abb]
            if type(next_m_config) != str:
                if next_m_config in cls.obj2name:
                    next_m_config = cls.obj2name[next_m_config]
                else:
                    cls.obj2name[next_m_config] = cls.next_m_config_name()
                    next_m_config = cls.obj2name[next_m_config]
            rule = TransitionRule(abb, symbol, operations, next_m_config)
            table.add_rule(rule)

        return table

    @classmethod
    def get_root(cls, dict, state):
        while state in dict:
            state = dict[state]

        return state


class abbreviatedTable(metaclass=SkelotonCompiler):
    def __init__(self):
        self.transitions = []
        self.alias = None

    def add_transition(self, symbol, operations, next_m_config):
        if next_m_config in abbreviatedTable._instances:
            next_m_config = abbreviatedTable._instances[next_m_config]
        self.transitions.append((symbol, operations, next_m_config))
        return

    def set_alias(self, abbreviation):
        self.alias = abbreviation


class Find(abbreviatedTable):
    """
    find the first occurrence of alpha in the xed Figure square ont the tape
    transfer to success if alpha is found, otherwise transfer to fail
    """

    def __init__(self, success, fail, alpha):
        super().__init__()
        self.add_transition("$", ["L"], Find1(success, fail, alpha))
        self.add_transition("*", ["L"], self)


class Find1(abbreviatedTable):
    def __init__(self, success, fail, alpha):
        super().__init__()

        self.add_transition(alpha, [], success)
        self.add_transition("_", ["R"], Miss1(success, fail, alpha))
        self.add_transition("*", ["R"], self)


class Miss1(abbreviatedTable):
    def __init__(self, success, fail, alpha):
        super().__init__()

        self.add_transition(alpha, ["R"], success)
        self.add_transition("_", ["R"], fail)
        self.add_transition("*", ["R"], Find1(success, fail, alpha))


class Erase(abbreviatedTable):

    def __init__(self, *args):
        """
        if len(args) ==3:  erase the first occurrence of alpha in the tape and transition to success
        if alpha is not found, transition to fail

        if len(args) ==2:  erase all the occurrence of alpha in the tape and transition to success
        """
        super().__init__()
        if len(args) == 3:
            success, fail, alpha = args
            self.set_alias(Find(Erase1(success, fail, alpha), fail, alpha))
        elif len(args) == 2:
            success, alpha = args
            self.set_alias(Erase(Erase(success, alpha), success, alpha))


class Erase1(abbreviatedTable):
    def __init__(self, success, fail, alpha):
        super().__init__()
        self.add_transition(alpha, ["_"], success)


class PrintEnd(abbreviatedTable):
    """
    append alpha to the end of tape (first nonempty Figure square)
    """

    def __init__(self, success, beta):
        super().__init__()
        self.set_alias(Find(PrintEnd1(success, beta), success, "$"))


class PrintEnd1(abbreviatedTable):
    def __init__(self, success, beta):
        super().__init__()
        self.add_transition("_", [beta], success)
        self.add_transition("*", ["R", "R"], self)


class Left(abbreviatedTable):
    def __init__(self, success):
        super().__init__()
        self.add_transition("*", ["L"], success)


class Right(abbreviatedTable):
    def __init__(self, success):
        super().__init__()
        self.add_transition("*", ["R"], success)


class FindThenLeft(abbreviatedTable):
    def __init__(self, success, fail, alpha):
        super().__init__()
        self.set_alias(Find(Left(success), fail, alpha))


class FindThenRight(abbreviatedTable):
    def __init__(self, success, fail, alpha):
        super().__init__()
        self.set_alias(Find(Right(success), fail, alpha))


class Copy(abbreviatedTable):
    def __init__(self, success, fail, x):
        """
        copy the xed figure to the end empty figure of the tape
        """
        super().__init__()
        self.set_alias(FindThenLeft(Copy1(success), fail, x))


class Copy1(abbreviatedTable):
    def __init__(self, success):
        super().__init__()
        self.add_transition("1", [], PrintEnd(success, "1"))
        self.add_transition("0", [], PrintEnd(success, "0"))


class CopyThenErase(abbreviatedTable):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 3:
            # copy the markeded figure to the end empty figure of the tape and erase the x
            success, fail, x = args
            self.set_alias(Copy(Erase(success, fail, x), fail, x))
        elif len(args) == 2:
            # copy all marked figures to the end empty figures of the tape and erase all x
            success, x = args
            self.set_alias(
                CopyThenErase(CopyThenErase(success, x), success, x)
            )


class Replace(abbreviatedTable):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 4:
            #  replaces the first  alpha by beta and -> success or -> fail if there is no alpha
            success, fail, alpha, beta = args
            self.set_alias(Find(Replace1(success, beta), fail, alpha))
        elif len(args) == 3:
            # replaces all the occurrence of alpha by beta and -> success
            success, alpha, beta = args
            self.set_alias(
                Replace(Replace(success, alpha, beta), success, alpha, beta)
            )


class Replace1(abbreviatedTable):
    def __init__(self, success, beta):
        super().__init__()
        self.add_transition("*", ["_", beta], success)


class CopyThenReplace(abbreviatedTable):
    """
    This is the same as copy, this is just a test to the combination of the abbreviated tables
    """

    def __init__(self, *args):
        super().__init__()
        if len(args) == 3:
            success, fail, x = args
            self.set_alias(Copy(Replace(success, fail, x, x), fail, x))
        elif len(args) == 2:
            success, x = args
            self.set_alias(
                CopyThenReplace(
                    CopyThenReplace(success, x),
                    CopyThenReplace(success, x, x),
                    x,
                )
            )


class Compare(abbreviatedTable):
    def __init__(self, success, fail, miss, x, y):
        """
        compare the markedd figures and transfer to success if they are equal, otherwise transfer to fail

        if x and y is not found, transfer to miss, if one of them is not found, transfer to fail
        """
        super().__init__()
        self.set_alias(FindThenLeft(Compare1(success, fail, y), miss, x))


class Compare1(abbreviatedTable):
    def __init__(self, success, fail, y):
        """
        find x
        """
        super().__init__()
        self.add_transition(
            "0", [], FindThenLeft(Compare2(success, fail, "0"), fail, y)
        )
        self.add_transition(
            "1", [], FindThenLeft(Compare2(success, fail, "1"), fail, y)
        )


class Compare2(abbreviatedTable):
    def __init__(self, success, fail, alpha):
        super().__init__()
        if alpha == "0":
            self.add_transition("0", [], success)
            self.add_transition("*", [], fail)
        elif alpha == "1":
            self.add_transition("1", [], success)
            self.add_transition("*", [], fail)


class CompareThenErase(abbreviatedTable):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 5:
            success, fail, miss, x, y = args
            self.set_alias(
                Compare(
                    Erase(Erase(success, success, x), success, y),
                    fail,
                    miss,
                    x,
                    y,
                )
            )
        elif len(args) == 4:
            # compare all and erase all marks, goto  miss after all erase, else goto  fail
            fail, miss, x, y = args
            self.set_alias(
                CompareThenErase(
                    CompareThenErase(fail, miss, x, y), fail, miss, x, y
                )
            )


class FindRight(abbreviatedTable):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            # goto the end of tape (two consecutive empty figures are the end of the tape)
            success = args[0]
            self.add_transition("*", ["R"], FindRight(success))
            self.add_transition("_", ["R"], FindRight1(success))
        elif len(args) == 2:
            # goto the end of tape then search back to the first alpha
            success, alpha = args
            self.set_alias(FindRight(FindRight1(success, alpha)))


class FindRight1(abbreviatedTable):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            success = args[0]
            self.add_transition("_", [], success)
            self.add_transition("*", ["R"], self)
        elif len(args) == 2:
            success, alpha = args
            self.add_transition("*", ["L"], self)
            self.add_transition(alpha, [], success)


class PrintEndTwo(abbreviatedTable):
    """
    append alpha to the end of tape, then append beta to the end of the tape
    """

    def __init__(self, success, alpha, beta):
        super().__init__()
        self.set_alias(PrintEnd(PrintEnd(success, beta), alpha))


class CopyThenEraseTwo(abbreviatedTable):
    """
    copy all the figures marked by x to the end of tape then erase all x

    copy all the figures makred by y to the end of tape then erase all y
    """

    def __init__(self, success, x, y):
        super().__init__()
        self.set_alias(CopyThenErase(CopyThenErase(success, y), x))


class CopyThenEraseThree(abbreviatedTable):
    """
    copy all the figures marked by x to the end of tape then erase all x

    copy all the figures makred by y to the end of tape then erase all y

    copy all the figures makred by z to the end of tape then erase all z
    """

    def __init__(self, success, x, y, z):
        super().__init__()
        self.set_alias(CopyThenErase(CopyThenEraseTwo(success, y, z), x))


class EraseAllMark(abbreviatedTable):
    def __init__(self, success):
        super().__init__()
        self.add_transition("*", ["L"], self)
        self.add_transition("$", ["R"], EraseAllMark1(success))


class EraseAllMark1(abbreviatedTable):
    def __init__(self, success):
        super().__init__()
        self.add_transition("*", ["R", "_", "R"], self)
        self.add_transition("_", [], success)


def generate_builtin_library():
    find = Find("a", "b", "x")
    erase = Erase("a", "b", "x")


#  Test Cases


def test_compile_erase():
    from pprint import pprint

    SkelotonCompiler.reset()
    e = Erase("a", "1")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "1", "R", "x", "R", "1", "R", "x"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=30, verbose=True)
    print(tm.get_tape())
    return tm


def test_compile_print_end():
    from pprint import pprint

    pprint("test_compile_print_end")

    SkelotonCompiler.reset()
    e = PrintEnd("a", "1")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "0", "R", "x"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=11, verbose=True)
    print(tm.get_tape())
    return tm


def test_compile_find_and_move():
    from pprint import pprint

    pprint("test_find_and_move")

    SkelotonCompiler.reset()
    e = FindThenLeft(FindThenRight("a", "b", "x"), "b", "0")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "0", "R", "x"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=16, verbose=True)
    print(tm.get_tape())
    return tm


def test_compile_copy_erase():
    from pprint import pprint

    pprint("test copy xed and erase x")

    SkelotonCompiler.reset()
    e = CopyThenErase("a", "x")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "0", "R", "x"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=70, verbose=True)
    print(tm.get_tape())
    return tm


def test_compile_replace():
    from pprint import pprint

    pprint("test replace all alpha")

    SkelotonCompiler.reset()
    e = Replace("a", "0", "1")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "0", "R", "x"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=30, verbose=True)
    print(tm.get_tape())
    return tm


def test_compile_copy_replace():
    from pprint import pprint

    pprint("test copy then replace")

    SkelotonCompiler.reset()
    e = CopyThenReplace("a", "x")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "0", "R", "x"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=70, verbose=True)
    print(tm.get_tape())
    return tm


def test_compile_compare():
    from pprint import pprint

    pprint("test compare and success")

    SkelotonCompiler.reset()
    e = Compare("success", "fail", "miss", "x", "y")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "0", "R", "y"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=22, verbose=True)
    print(tm.get_tape())
    print(tm.m_configuration)

    pprint("test compare and failed")
    SkelotonCompiler.reset()
    e = Compare("success", "fail", "miss", "x", "y")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "1", "R", "y"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=22, verbose=True)
    print(tm.get_tape())
    print(tm.m_configuration)
    return tm


def test_compile_compare_then_erase_all():
    from pprint import pprint

    pprint("test compare and success erase all x and y")

    SkelotonCompiler.reset()
    e = CompareThenErase("fail", "miss", "x", "y")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            [
                "$",
                "R",
                "$",
                "R",
                "0",
                "R",
                "x",
                "R",
                "0",
                "R",
                "x",
                "R",
                "0",
                "R",
                "y",
                "R",
                "0",
                "R",
                "y",
            ],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=133, verbose=False)
    print(tm.get_tape())
    print(tm.m_configuration)


def test_compile_find_right():
    from pprint import pprint

    pprint("test find the right most x")

    SkelotonCompiler.reset()
    e = FindRight("success", "x")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "L", "L", "L"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=9, verbose=True)
    print(tm.get_tape())
    assert tm.m_configuration == "success", tm.m_configuration
    return tm


def test_compile_copy_then_erase_three():
    from pprint import pprint

    pprint("test copy all figures marked as x,y,z to the end of tape")

    SkelotonCompiler.reset()
    e = CopyThenEraseThree("success", "x", "y", "z")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule("b", "_", ["$", "R", "$", "R", "0", "R", "x", "R"], "c")
    )
    table.add_rule(
        TransitionRule(
            "c",
            "_",
            ["1", "R", "y", "R", "1", "R", "y", "R"],
            "d",
        )
    )
    table.add_rule(
        TransitionRule(
            "d",
            "_",
            ["0", "R", "z", "R", "0", "R", "z", "R", "0", "R", "z", "R"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=519, verbose=False)
    print(tm.get_sequence())
    assert tm.m_configuration == "success", tm.m_configuration
    return tm


def test_compile_erase_all_marks():
    from pprint import pprint

    pprint("test erase all marks ")

    SkelotonCompiler.reset()
    e = EraseAllMark("success")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "0", "R", "x", "R", "0", "R", "x"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.run(steps=9, verbose=True)
    print(tm.get_sequence())
    assert tm.m_configuration == "success", tm.m_configuration
    return tm


if __name__ == "__main__":

    test_compile_erase()
    test_compile_print_end()
    test_compile_find_and_move()
    test_compile_copy_erase()
    test_compile_replace()
    test_compile_copy_replace()
    test_compile_compare()
    test_compile_compare_then_erase_all()
    test_compile_find_right()
    test_compile_copy_then_erase_three()
    test_compile_erase_all_marks()
