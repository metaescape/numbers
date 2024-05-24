"""
This script almost reproduces Chapter 7, "Detailed description of the universal machine" from Turing's 1936 paper.

Use the library defined in "abbreviated.py" to build a universal machine.

There are different universal machines for different types of encoding. 

The universal machine in this script is designed for interpreting the standard encoding of the transition table.

Author: Metaesc
Email: metaescape@foxmail.com
License: MIT License
"""

try:
    from turing_machine.op_extend import Table, TransitionRule, TuringMachine
    from turing_machine.abbreviated import (
        SkelotonCompiler,
        FindRight,
        EraseAllMark,
        Compare,
        abbreviatedTable,
    )
    from turing_machine.encoding import Encoder
except:
    from op_extend import Table, TransitionRule, TuringMachine
    from abbreviated import (
        SkelotonCompiler,
        FindRight,
        EraseAllMark,
        Compare,
        abbreviatedTable,
    )
    from encoding import Encoder


class MarkRightConfig(abbreviatedTable):
    """
    start from a Figure square, mark all the symbol in the first m-configuration( e.g DAAAA) to the right using x
    """

    def __init__(self, success, x):
        super().__init__()
        self.add_transition("A", ["L", x, "R"], MarkRightConfig1(success, x))
        self.add_transition("*", ["R", "R"], self)


class MarkRightConfig1(abbreviatedTable):
    def __init__(self, success, x):
        super().__init__()
        self.add_transition("A", ["R", x, "R"], MarkRightConfig1(success, x))
        self.add_transition("D", ["R", x, "R"], MarkRightConfig2(success, x))
        self.add_transition("_", ["D", "R", x, "R", "R", "R"], success)


class MarkRightConfig2(abbreviatedTable):
    def __init__(self, success, x):
        super().__init__()
        self.add_transition("C", ["R", x, "R"], MarkRightConfig2(success, x))
        self.add_transition("*", ["R", "R"], success)


def begin_of_universal():
    return


def show_1_3_table_description():
    """
    The first example from Turing Paper 1936, this is the description of a turing machine
    Compare to the same 1/3 table in basic.py, we use "_" to replace the None in the symbol field
    """
    from pprint import pprint

    pprint(
        "show the standard description for the turing machine that print 1/3 in binary"
    )
    bcek_table = Table()

    bcek_table.add_rule(TransitionRule("b", "_", ["0", "R"], "c"))
    bcek_table.add_rule(TransitionRule("c", "_", ["_", "R"], "e"))
    bcek_table.add_rule(TransitionRule("e", "_", ["1", "R"], "k"))
    bcek_table.add_rule(TransitionRule("k", "_", ["_", "R"], "b"))

    tm = TuringMachine(bcek_table, "b")
    tm.run(steps=5, verbose=False)
    print(tm.get_history())

    encoder = Encoder(bcek_table, {"0", "1", "$"}, {"_", "x"})

    tm = TuringMachine(encoder.std_form_table, encoder.get_inner_m_config("b"))
    pprint(encoder.std_form_table)
    tm.run(steps=5, verbose=False)
    print("tape history in normal form:")
    print(tm.get_history())
    print("tape history in standard encoding:")
    print(encoder.encode_history(tm.history))
    print("compare to its standard description:")
    pprint(encoder.standard_description)
    print("and its 5-tuple form:")
    print(encoder.standard_form)


def add_1_3_code_to_machine():
    from pprint import pprint

    pprint("load 1/3 machine code to the tape of another machine")
    bcek_table = Table()

    bcek_table.add_rule(TransitionRule("b", "_", ["0", "R"], "c"))
    bcek_table.add_rule(TransitionRule("c", "_", ["1", "R"], "b"))

    encoder = Encoder(bcek_table, {"0", "1", "$"}, {"_", "x"})
    print(encoder.standard_description)
    tm = TuringMachine({}, "b")
    tm.load_instruction(encoder.standard_description)
    print(tm.get_tape())


def test_mark_right():
    from pprint import pprint

    pprint("test MarkRightConfig function")
    bcek_table = Table()

    bcek_table.add_rule(TransitionRule("b", "_", ["0", "R"], "c"))
    bcek_table.add_rule(TransitionRule("c", "_", ["1", "R"], "b"))
    encoder = Encoder(bcek_table, {"0", "1", "$"}, {"_", "x"})

    SkelotonCompiler.reset()
    e = MarkRightConfig("success", "x")
    table = SkelotonCompiler.compile()
    table.add_rule(
        TransitionRule(
            "b",
            "*",
            ["R", "R"],
            SkelotonCompiler.get_m_config_name(e),
        )
    )

    pprint(table.table)
    tm = TuringMachine(table, "b")
    tm.load_instruction(encoder.standard_description)
    tm.run(steps=7, verbose=True)
    return tm


if __name__ == "__main__":
    show_1_3_table_description()
    add_1_3_code_to_machine()
    test_mark_right()
