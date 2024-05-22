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
    )
    from turing_machine.encoding import Encoder
except:
    from op_extend import Table, TransitionRule, TuringMachine
    from abbreviated import SkelotonCompiler, FindRight, EraseAllMark, Compare
    from encoding import Encoder


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
    pprint(encoder.standard_description)

    tm = TuringMachine(encoder.std_form_table, encoder.get_inner_m_config("b"))
    pprint(encoder.std_form_table)
    tm.run(steps=5, verbose=False)
    print("tape history in normal form:")
    print(tm.get_history())
    print("tape history in standard encoding:")
    print(encoder.encode_history(tm.history))


if __name__ == "__main__":
    show_1_3_table_description()
