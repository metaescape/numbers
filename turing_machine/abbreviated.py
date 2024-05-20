"""
Manually Implement the abbreviated Tables
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
        """
        table = Table()
        rules = []

        alias_map = cls.build_alias_map()

        for abb in cls._instances2name.keys():
            for symbol, operations, next_m_config in abb.transitions:
                if abb in alias_map:
                    abb = get_root(alias_map, abb)
                if next_m_config in alias_map:
                    next_m_config = get_root(alias_map, next_m_config)
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


def get_root(dict, key):
    while key in dict:
        key = dict[key]
    return key


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
    find the first occurrence of alpha in the tape and transition to state1
    if alpha is not found, transition to state2
    """

    def __init__(self, state1, state2, alpha):
        super().__init__()
        self.add_transition("$", ["L"], Find1(state1, state2, alpha))
        self.add_transition("*", ["L"], self)


class Find1(abbreviatedTable):
    def __init__(self, state1, state2, alpha):
        super().__init__()

        self.add_transition(alpha, [], state1)
        self.add_transition("_", ["R"], Find2(state1, state2, alpha))
        self.add_transition("*", ["R"], self)


class Find2(abbreviatedTable):
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


def generate_builtin_lib():
    find = Find("a", "b", "x")
    erase = Erase("a", "b", "x")


def test_compile_erase_1s():
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
    tm.run(steps=100, verbose=True)
    print(tm.get_tape())
    return tm


if __name__ == "__main__":

    test_compile_erase_1s()
