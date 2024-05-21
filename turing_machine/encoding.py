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
        Compare,
    )
except:
    from op_extend import Table, TransitionRule, TuringMachine
    from abbreviated import SkelotonCompiler, FindRight, EraseAllMark, Compare


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
        self.vocab = figure_vocab | erase_vocab
        self.std_map = self.build_symbol_map()
        self.max_m_config_number = self.get_max_m_config_number()
        self.symbol_expanded_table = self.expand_regex_in_table(table.table)
        self.m_config_std_table = self.standardize_m_configuration(
            self.symbol_expanded_table.table, self.max_m_config_number + 1
        )

    def build_symbol_map(self):
        std_code_map = {
            "_": "D",
            "0": "DC",
            "1": "DCC",
            "$": "DCCC",
            "x": "DCCCC",
        }
        cnt = 5
        for symbol in self.vocab:
            if symbol not in std_code_map:
                std_code_map[symbol] = "D" + cnt * "C"
                cnt += 1
        return std_code_map

    def get_max_m_config_number(self):
        max_number = 0
        for key, _ in self.origin_table.table.items():
            m_config, _ = key
            if m_config.startswith("q"):
                number = int(m_config[1:])
                max_number = max(max_number, number)
        return max_number

    def expand_any_regex_symbol(self, rule: TransitionRule):
        """
        Expand the * symbol to all possible symbols
        """
        rules = []
        assert "*" in rule.symbols
        for symbol in self.vocab:
            if (rule.m_config, symbol) not in self.origin_table.table:
                new_rule = TransitionRule(
                    rule.m_config, symbol, rule.operations, rule.next_m_config
                )
                rules.append(new_rule)

        return rules

    def expand_regex_in_table(self, table: dict):
        """
        Expand the * symbol in the table
        """
        new_table = Table()
        for key, value in table.items():
            rule = TransitionRule(key[0], key[1], value[0], value[1])
            if "*" in rule.symbols:
                rules = self.expand_any_regex_symbol(rule)
                for new_rule in rules:
                    new_table.add_rule(new_rule)
            else:
                new_table.add_rule(rule)

        return new_table

    def standardize_m_configuration(self, table: dict, cnt: int):
        """
        make sure the m_configuration is in the form of q1, q2, q3, ...
        """
        self.name_map = {}
        new_table = Table()
        for key, value in table.items():
            m_config, symbol = key
            operations, next_m_config = value
            if not m_config.startswith("q"):
                if m_config not in self.name_map:
                    self.name_map[m_config] = "q" + str(cnt)
                    cnt += 1
                m_config = self.name_map[m_config]
            if not next_m_config.startswith("q"):
                if next_m_config not in self.name_map:
                    self.name_map[next_m_config] = "q" + str(cnt)
                    cnt += 1
                next_m_config = self.name_map[next_m_config]

            new_table.add_rule(
                TransitionRule(m_config, symbol, operations, next_m_config)
            )

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


def test_expand_any_regex_symbol():
    from pprint import pprint

    pprint("test expand any regex symbol")

    rule = TransitionRule("q2", "*", ["R", "_", "R"], "q2")
    e = EraseAllMark("success")
    table = SkelotonCompiler.compile()
    encoder = Encoder(table, {"0", "1"}, {"_", "x"})

    rules = encoder.expand_any_regex_symbol(rule)
    pprint(rules)

    pprint(encoder.symbol_expanded_table)


def test_symbol_from_current_head():
    from pprint import pprint

    pprint("test_symbol_from_current_head")

    SkelotonCompiler.reset()
    SkelotonCompiler.set_vocab({"0", "1", "a", "b"})
    e = Compare("success", "fail", "miss", "x", "y")

    table = SkelotonCompiler.compile()

    pprint(table)
    assert ("q1", "a") in table

    # pprint(encoder.symbol_expanded_table)


def test_m_config_name_normalize():
    from pprint import pprint

    pprint("test_m_config_name_normalize ")

    SkelotonCompiler.reset()
    e = FindRight("success", "x")
    table = SkelotonCompiler.compile()
    table.add_rule(TransitionRule("b", "_", ["$", "R", "$", "R"], "c"))
    table.add_rule(
        TransitionRule("c", "_", [], SkelotonCompiler.get_m_config_name(e))
    )

    encoder = Encoder(table, {"0", "1"}, {"_", "x"})
    pprint(encoder.m_config_std_table)
    pprint(encoder.name_map["b"])


if __name__ == "__main__":
    test_max_m_config_number()
    test_expand_any_regex_symbol()
    test_symbol_from_current_head()
    test_m_config_name_normalize()
