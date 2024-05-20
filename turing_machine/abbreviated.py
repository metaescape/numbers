"""
Manually Implement the abbreviated Tables and a Turing Machine with runtime transition rules
"""

from turing_machine.op_extend import Table, TransitionRule, TuringMachine


class SkelotonCompiler(type):
    """
    This is a metaclass to implement the singleton pattern.
    it is also a compiler to translate the high level abbreviated tables which are the instances of AbbreviatedTable
    to the low level transition rules which can be executed by the original Turing Machine
    """

    _instances: dict = {}
    _instances2name: dict = {}
    cnt = 0
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
        cls.cnt = 0
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
    find the first occurrence of alpha in the marked Figure square ont the tape
    transfer to state1 if alpha is found, otherwise transfer to state2
    """

    def __init__(self, state1, state2, alpha):
        super().__init__()
        self.add_transition("$", ["L"], Find1(state1, state2, alpha))
        self.add_transition("*", ["L"], self)


class Find1(abbreviatedTable):
    def __init__(self, state1, state2, alpha):
        super().__init__()

        self.add_transition(alpha, [], state1)
        self.add_transition("_", ["R"], Miss1(state1, state2, alpha))
        self.add_transition("*", ["R"], self)


class Miss1(abbreviatedTable):
    def __init__(self, state1, state2, alpha):
        super().__init__()

        self.add_transition(alpha, ["R"], state1)
        self.add_transition("_", ["R"], state2)
        self.add_transition("*", ["R"], Find1(state1, state2, alpha))


class Erase(abbreviatedTable):

    def __init__(self, *args):
        """
        if len(args) ==3:  erase the first occurrence of alpha in the tape and transition to state1
        if alpha is not found, transition to state2

        if len(args) ==2:  erase all the occurrence of alpha in the tape and transition to state1
        """
        super().__init__()
        if len(args) == 3:
            state1, state2, alpha = args
            self.set_alias(Find(Erase1(state1, state2, alpha), state2, alpha))
        elif len(args) == 2:
            state1, alpha = args
            self.set_alias(Erase(Erase(state1, alpha), state1, alpha))


class Erase1(abbreviatedTable):
    def __init__(self, state1, state2, alpha):
        super().__init__()
        self.add_transition(alpha, ["_"], state1)


class PrintEnd(abbreviatedTable):
    def __init__(self, state1, beta):
        super().__init__()
        self.set_alias(Find(PrintEnd1(state1, beta), state1, "$"))


class PrintEnd1(abbreviatedTable):
    def __init__(self, state1, beta):
        super().__init__()
        self.add_transition("_", [beta], state1)
        self.add_transition("*", ["R", "R"], self)


class Left(abbreviatedTable):
    def __init__(self, state1):
        super().__init__()
        self.add_transition("*", ["L"], state1)


class Right(abbreviatedTable):
    def __init__(self, state1):
        super().__init__()
        self.add_transition("*", ["R"], state1)


class FindThenLeft(abbreviatedTable):
    def __init__(self, state1, state2, alpha):
        super().__init__()
        self.set_alias(Find(Left(state1), state2, alpha))


class FindThenRight(abbreviatedTable):
    def __init__(self, state1, state2, alpha):
        super().__init__()
        self.set_alias(Find(Right(state1), state2, alpha))


class Copy(abbreviatedTable):
    def __init__(self, state1, state2, mark):
        super().__init__()
        self.set_alias(FindThenLeft(Copy1(state1), state2, mark))


class Copy1(abbreviatedTable):
    def __init__(self, state1):
        super().__init__()
        self.add_transition("1", [], PrintEnd(state1, "1"))
        self.add_transition("0", [], PrintEnd(state1, "0"))


class CopyThenErase(abbreviatedTable):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 3:
            state1, state2, alpha = args
            self.set_alias(Copy(Erase(state1, state2, alpha), state2, alpha))
        elif len(args) == 2:
            state1, alpha = args
            self.set_alias(
                CopyThenErase(CopyThenErase(state1, alpha), state1, alpha)
            )


def generate_builtin_library():
    find = Find("a", "b", "x")
    erase = Erase("a", "b", "x")


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

    pprint("test copy marked and erase mark")

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


if __name__ == "__main__":

    test_compile_erase()
    test_compile_print_end()
    test_compile_find_and_move()
    test_compile_copy_erase()
