"""
This script almost reproduces Chapter 7, "Detailed description of the universal machine" from Turing's 1936 paper.

Using the library defined in "abbreviated.py" to build a universal machine.

Note:

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
        Find,
        FindRight,
        EraseAllMark,
        AbbreviatedTable,
        CompareThenErase,
        Erase,
        FindThenLeft,
        Left,
        PrintEndTwo,
        CopyThenEraseThree,
        CopyThenEraseTwo,
    )
    from turing_machine.encoding import Encoder
except:
    from op_extend import Table, TransitionRule, TuringMachine
    from abbreviated import (
        SkelotonCompiler,
        Find,
        FindRight,
        EraseAllMark,
        AbbreviatedTable,
        CompareThenErase,
        Erase,
        FindThenLeft,
        Left,
        PrintEndTwo,
        CopyThenEraseThree,
        CopyThenEraseTwo,
    )
    from encoding import Encoder


class MarkRightConfig(AbbreviatedTable):
    """
    con stat in the paper
    start from a Figure square, mark the first m-configuration and symbol sequence( e.g DAAAADCC) to the right using x
    """

    def __init__(self, success, x):
        super().__init__()
        self.add_transition("A", ["L", x, "R"], MarkRightConfig1(success, x))
        self.add_transition("*", ["R", "R"], self)


class MarkRightConfig1(AbbreviatedTable):
    def __init__(self, success, x):
        super().__init__()
        self.add_transition("A", ["R", x, "R"], MarkRightConfig1(success, x))
        self.add_transition("D", ["R", x, "R"], MarkRightConfig2(success, x))
        self.add_transition("_", ["D", "R", x, "R", "R", "R"], success)


class MarkRightConfig2(AbbreviatedTable):
    def __init__(self, success, x):
        super().__init__()
        self.add_transition("C", ["R", x, "R"], MarkRightConfig2(success, x))
        self.add_transition("*", ["R", "R"], success)


class EntryUTM(AbbreviatedTable):
    """
    the fisrt state of the universal machine
    """

    def __init__(self):
        super().__init__()
        self.add_transition("*", "R", Find(EntryUTM1(), EntryUTM1(), "::"))


class EntryUTM1(AbbreviatedTable):
    def __init__(self):
        super().__init__()
        self.add_transition(
            "*",
            ["R", "R", ":", "R", "R", "D", "R", "R", "A"],
            MarkLastConfig(),
        )  # print q1 state to tape,so this should be the first state of any machine


class MarkLastConfig(AbbreviatedTable):
    """
    anf state in the paper
    """

    def __init__(self):
        super().__init__()
        self.set_alias(FindRight(MarkLastConfig1(), ":"))


class MarkLastConfig1(AbbreviatedTable):
    def __init__(self):
        super().__init__()
        self.set_alias(MarkRightConfig(MarkNextConfig(), "y"))


class MarkNextConfig(AbbreviatedTable):
    """
    kom state in the paper
    """

    def __init__(self):
        super().__init__()
        self.add_transition(
            ";", ["R", "z", "L"], MarkRightConfig(CompareXYSequence(), "x")
        )
        self.add_transition("z", ["L", "L"], self)
        self.add_transition("*", ["L"], self)


class CompareXYSequence(AbbreviatedTable):
    """kmp state in the paper"""

    def __init__(self):
        super().__init__()
        self.set_alias(
            CompareThenErase(
                Erase(Erase(MarkLastConfig(), "x"), "y"), SAME(), "x", "y"
            )
        )


class SAME(AbbreviatedTable):
    """sim state in the paper
    mark next-m-configuration in the instruction with y
    """

    def __init__(self):
        super().__init__()
        self.set_alias(FindThenLeft(SAME1(), SAME2(), "z"))


class SAME1(AbbreviatedTable):
    """sim1 state in the paper"""

    def __init__(self):
        super().__init__()
        self.set_alias(MarkRightConfig(SAME2(), ""))


class SAME2(AbbreviatedTable):
    """sim2 state in the paper"""

    def __init__(self):
        super().__init__()
        self.add_transition("A", [], SAME3())
        self.add_transition("*", ["L", "u", "R", "R", "R"], self)


class SAME3(AbbreviatedTable):
    """sim3 state in the paper"""

    def __init__(self):
        super().__init__()

        self.add_transition("A", ["L", "y", "R", "R", "R"], self)
        self.add_transition("*", ["L", "y"], Erase(MarkLastFullConfig(), "z"))


class MarkLastFullConfig(AbbreviatedTable):
    """
    mk/mf state in the paper, FullConfig is the same as Complete configuration
    this state will mark the sequence left to the m-configuation and current symbol in the last complete configuration with x
    also mark the sequence right to the m-configuation and current symbol in the last complete configuration with v

    """

    def __init__(self):
        super().__init__()
        self.set_alias(FindRight(MarkLastFullConfig1(), ":"))


class MarkLastFullConfig1(AbbreviatedTable):

    def __init__(self):
        super().__init__()
        self.add_transition(
            "A", ["L"] * 4, MarkLastFullConfig2()
        )  # find c-config
        self.add_transition("*", ["R"] * 2, self)


class MarkLastFullConfig2(AbbreviatedTable):
    """
    mark the first DCCC.. to the left of m-configuation and current symbol in the last complete configuration with x
    """

    def __init__(self):
        super().__init__()
        self.add_transition("C", ["R", "x", "L", "L", "L"], self)
        self.add_transition(":", [], MarkLastFullConfig4())
        self.add_transition(
            "D", ["R", "x", "L", "L", "L"], MarkLastFullConfig3()
        )


class MarkLastFullConfig3(AbbreviatedTable):
    """
    Mark the remain DCC.. to the left o m-configuation in the last complete configuration with v
    """

    def __init__(self):
        super().__init__()
        self.add_transition(":", [], MarkLastFullConfig4())
        self.add_transition("*", ["R", "v", "L", "L", "L"], self)


class MarkLastFullConfig4(AbbreviatedTable):
    def __init__(self):
        super().__init__()
        self.set_alias(
            MarkRightConfig(Left(Left(MarkLastFullConfig5())), "")
        )  # skip the m-config and current symbol


class MarkLastFullConfig5(AbbreviatedTable):
    """
    Mark all the DCC.. sybmol to the right of m-configuration and current symbol in last complete configuration with w
    """

    def __init__(self):
        super().__init__()
        self.add_transition("_", [":"], Print0or1())
        self.add_transition("*", ["R", "w", "R"], self)


class Print0or1(AbbreviatedTable):
    """
    eb state in the paper
    go back to instruction section, if 1 or 0 is Printed in the  instruction, print it to the end of complete configuration
    """

    def __init__(self):
        super().__init__()
        self.set_alias(Find(Print0or1_1(), Inst(), "u"))


class Print0or1_1(AbbreviatedTable):
    """ """

    def __init__(self):
        super().__init__()
        # goto the last square of scanned symbol in  the instruction
        self.add_transition("*", ["L"] * 3, Print0or1_2())


class Print0or1_2(AbbreviatedTable):
    def __init__(self):
        super().__init__()
        self.add_transition("D", ["R"] * 4, Print0or1_3())
        self.add_transition("*", [], Inst())


class Print0or1_3(AbbreviatedTable):
    def __init__(self):
        super().__init__()
        self.add_transition("C", ["R"] * 2, Print0or1_4())
        self.add_transition("*", [], Inst())


class Print0or1_4(AbbreviatedTable):
    def __init__(self):
        super().__init__()
        self.add_transition("C", ["R"] * 2, Print0or1_5())
        self.add_transition("*", [], PrintEndTwo(Inst(), "0", ":"))


class Print0or1_5(AbbreviatedTable):
    def __init__(self):
        super().__init__()
        self.add_transition("C", ["R"] * 2, Print0or1_5())
        self.add_transition("*", [], PrintEndTwo(Inst(), "1", ":"))


class Inst(AbbreviatedTable):
    """
    inst state in the paper, create a new complete configuration base on the instruction and last complete configuration
    """

    def __init__(self):
        super().__init__()
        # find the action in the instruction
        self.set_alias(FindRight(Left(Inst1()), "u"))


class Inst1(AbbreviatedTable):
    def __init__(self):
        super().__init__()
        clean_and_restart = EraseAllMark(MarkLastConfig())
        self.add_transition(
            "L",
            ["R", "_"],
            CopyThenEraseFive(clean_and_restart, "v", "y", "x", "u", "w"),
        )
        self.add_transition(
            "R",
            ["R", "_"],
            CopyThenEraseFive(clean_and_restart, "v", "x", "u", "y", "w"),
        )
        self.add_transition(
            "N",
            ["R", "_"],
            CopyThenEraseFive(clean_and_restart, "v", "x", "y", "u", "w"),
        )


class CopyThenEraseFive(AbbreviatedTable):
    def __init__(self, success, x, y, z, u, v):
        super().__init__()
        self.set_alias(
            CopyThenEraseThree(CopyThenEraseTwo(success, u, v), x, y, z)
        )


def show_number_from_universal_tape(tm):
    seq = tm.get_sequence()
    number_seq = []
    for i in seq:
        if i in "01":
            number_seq.append(i)
    print(f"0 1 squence is: {number_seq}")
    result = 0
    for i in range(len(number_seq)):
        result += int(number_seq[i]) * 2 ** (-i - 1)
    print(f"decimal is: {result}")


def create_universal_machine(instruction):
    from pprint import pprint

    SkelotonCompiler.reset()
    SkelotonCompiler.set_vocab(
        {
            "0",
            "1",
            "R",
            "L",
            "N",
            "_",
            "x",
            "y",
            "z",
            "u",
            "v",
            "w",
            ":",
            ";",
            "D",
            "A",
            "C",
            "::",
        }
    )
    b = EntryUTM()
    table = SkelotonCompiler.compile()
    print(f"there are {SkelotonCompiler.cnt} states in the universal machine")
    tm = TuringMachine(table, SkelotonCompiler.get_m_config_name(b))
    tm.load_instruction(instruction)
    return tm


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

    pprint("---------test MarkRightConfig function----------")
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


def test_universal_machine():
    from pprint import pprint

    pprint("----------test universal machine----------")
    bcek_table = Table()
    bcek_table.add_rule(TransitionRule("b", "_", ["0", "R"], "c"))
    bcek_table.add_rule(TransitionRule("c", "_", ["1", "R"], "b"))
    encoder = Encoder(bcek_table, {"0", "1", "$"}, {"_", "x"})
    tm = create_universal_machine(encoder.standard_description)
    total = 50699
    tm.run(steps=total, verbose=range(total - 10, total))
    show_number_from_universal_tape(tm)
    return tm


if __name__ == "__main__":
    show_1_3_table_description()
    add_1_3_code_to_machine()
    test_mark_right()
    test_universal_machine()
