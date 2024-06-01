"""
A Scratch file for testing the quine turing machine (not fully implemented)
"""

try:
    from turing_machine.op_extend import Table, TransitionRule, TuringMachine
    from turing_machine.abbreviated import (
        SkelotonCompiler,
        AbbreviatedTable,
    )
    from turing_machine.encoding import Encoder
except:
    from op_extend import Table, TransitionRule, TuringMachine
    from abbreviated import (
        SkelotonCompiler,
        AbbreviatedTable,
    )
    from encoding import Encoder


def print_my_self():
    with open(__file__, "r") as f:
        lines = f.read()
        print(lines)


def create_print_self_machine():
    pass


class ForwardSearch(AbbreviatedTable):
    def __init__(self, success):
        super().__init__()


class PrintInst(AbbreviatedTable):
    def __init__(self, success, alpha):
        super().__init__()
        self.add_transition("$", [], FindFirstMark1(success, alpha))
        for alpha in SkelotonCompiler.vocab:
            if alpha != "$":
                self.add_transition(alpha, ["L"], self)


class FindFirstMark1(AbbreviatedTable):
    def __init__(self, success, alpha):
        super().__init__()
        self.add_transition(alpha, ["x", "L"], FindFirstMark2(success))
        for char in SkelotonCompiler.vocab:
            if char != alpha:
                self.add_transition(char, ["R", "R"], self)


class FindFirstMark2(AbbreviatedTable):
    def __init__(self, success):
        super().__init__()
        special = ["D", "N", "L", "R", "_"]
        self.add_transition("D", [], Copy2End(success, "P"))
        self.add_transition("N", [], Copy2End(success, "n"))
        self.add_transition("L", [], Copy2End(success, "l"))
        self.add_transition("R", [], Copy2End(success, "r"))
        self.add_transition("_", ["R", "_"], success)

        for char in SkelotonCompiler.vocab:
            if char not in special:
                self.add_transition(char, [], Copy2End(success, char))


class Copy2End(AbbreviatedTable):
    def __init__(self, success, alpha):
        super().__init__()
        self.add_transition("_", [alpha, "R", "y"], PrintInst(success, "_"))
        for char in SkelotonCompiler.vocab:
            if char != "_":
                self.add_transition(char, ["R", "R"], self)


def test_compile_copy_erase():
    from pprint import pprint

    pprint("test copy xed and erase x")

    SkelotonCompiler.reset()
    SkelotonCompiler.set_vocab(
        {"R", "L", "N", "_", "x", "y", "D", "A", "C", "$", "P", "p"}
    )
    e = PrintInst("success", "_")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "_",
            ["$", "R", "$", "R", "D", "R", "R", "A"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    convert_to_code(table)
    tm = TuringMachine(table, "b")
    tm.run(steps=50, verbose=True)
    print(tm.get_tape())

    return tm


def convert_to_code(table: Table):
    encoder = Encoder(
        table,
        {
            "R",
            "L",
            "N",
            "_",
            "x",
            "y",
            "D",
            "A",
            "C",
            "$",
            "P",
            "p",
            "n",
            "l",
            "r",
        },
        {"_", "x", "y"},
    )
    res = []
    print(len(encoder.standard_description))  # buggy, need to add new coding


# 调用函数
if __name__ == "__main__":
    print_my_self()
    test_compile_copy_erase()
