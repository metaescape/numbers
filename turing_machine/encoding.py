"""
This script almost reproduces Chapter 6, "Enumeration of Computable Sequences," from Turing's 1936 paper.

It implements the following utilities:
- Standard description of a Turing machine(aka table with 5-tuple descriptions)
- Description number of a Turing machine
- Standard rules (N1, N2, N3) of the transition table

Just as we can compile high-level languages to low-level languages at different optimization levels, 
we can compile abbreviated transition tables with different encoding levels, such as:
- 5-tuple description, e.g., q0 S1 PS1 R q1
  This means the state q0 reads the symbol S1, writes the symbol PS1, moves the tape to the right, and transitions to the state q1.
- Standard description level (using D, A, C to represent all symbols and state names)

The encoding level affects the simplicity and conciseness of the logical description, not the computational efficiency.

no need to modify the implementation of the Turing machine,
only add additional functions to compile the transition table secondarily.


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
    )
except:
    from op_extend import Table, TransitionRule, TuringMachine
    from abbreviated import SkelotonCompiler, FindRight, EraseAllMark


class Encoder:
    def __init__(
        self, table: Table, figure_vocab: set, erase_vocab: set
    ) -> None:
        """
        figure_vocab: the vocabulary of the figure squares, e.g., "0", "1"
        erase_vocab: the vocabulary of the erase squares, e.g., "_", "x", "y", "z"
        """
        self.origin_table = table
        self.figure_vocab = figure_vocab
        self.erase_vocab = erase_vocab
        self.build_symbol_map()
        self.max_m_config_number = self.get_max_m_config_number()

    def build_symbol_map(self):
        self.std_map = {
            "_": "D",
            "0": "DC",
            "1": "DCC",
            "$": "DCCC",
            "x": "DCCCC",
        }
        cnt = 5
        for symbol in self.figure_vocab | self.erase_vocab:
            if symbol not in self.std_map:
                self.std_map[symbol] = "D" + cnt * "C"
                cnt += 1

    def get_max_m_config_number(self):
        max_number = 0
        for key, _ in self.origin_table.table.items():
            m_config, _ = key
            if m_config.startswith("q"):
                number = int(m_config[1:])
                max_number = max(max_number, number)
        return max_number

    def standardize_m_configuration(self):
        """
        make sure the m_configuration is in the form of q1, q2, q3, ...
        """
        new_table = Table()
        for key, value in self.origin_table.table.items():
            m_config, symbol = key
            new_m_config = self.encode_m_config(m_config)
            new_key = (new_m_config, symbol)
            new_table.table[new_key] = value

        return new_table

    def encode_rule_to_5_tuple(self, rule: TransitionRule):
        """
        Encode the transition rule into 5-tuple description
        e.g. (b, "_", ["$", "R", "$", "R", ], "c") -> (b, None, 0, R, c)
        """
        pass

    def standard_encoding(self):
        """
        Encode the transition table into standard description
        """
        new_table = Table()
        pass
        return new_table

    def encode_description_number(self):
        """
        Encode the transition table into the description number
        """
        pass

    def encode_m_config(self, m_config: str):
        number = int(m_config[1:])
        return "D" + "A" * number

    def encode_symbol(self, symbol: str):
        return self.std_map[symbol]


# Test Cases


def test_max_m_config_number():
    from pprint import pprint

    pprint("test find the right most x")

    SkelotonCompiler.reset()
    e = EraseAllMark("success")
    table = SkelotonCompiler.compile()

    encoder = Encoder(table, {"0", "1"}, {"_", "x"})
    pprint(table.table)
    assert encoder.max_m_config_number == 2


if __name__ == "__main__":
    test_max_m_config_number()
