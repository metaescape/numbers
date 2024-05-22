"""
This script almost reproduces Chapter 6, "Enumeration of Computable Sequences," from Turing's 1936 paper.

It implements the following utilities:
- Standard form of a Turing machine(aka table with rules in 5-tuple format)
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
        self.q_cnt = self.get_max_m_config_number()
        self.symbol_expanded_table = self.expand_regex_in_table(table.table)
        self.m_config_std_table = self.standardize_m_configuration(
            self.symbol_expanded_table.table
        )
        self.std_form_table = self.encode_rule_to_5_tuple(
            self.m_config_std_table
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

    def standardize_m_configuration(self, table: dict):
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
                    self.q_cnt += 1
                    self.name_map[m_config] = "q" + str(self.q_cnt)
                m_config = self.name_map[m_config]
            if not next_m_config.startswith("q"):
                if next_m_config not in self.name_map:
                    self.q_cnt += 1
                    self.name_map[next_m_config] = "q" + str(self.q_cnt)
                next_m_config = self.name_map[next_m_config]

            new_table.add_rule(
                TransitionRule(m_config, symbol, operations, next_m_config)
            )

        return new_table

    def expand_operations(self, rule: TransitionRule) -> list:
        """
        Encode the transition rule into multiple 5-tuple form
        """
        operations = rule.operations
        if len(operations) == 0:
            return [
                TransitionRule(
                    rule.m_config,
                    rule.symbols,
                    [rule.symbols, "N"],
                    rule.next_m_config,
                )
            ]
        elif len(operations) == 1:
            if operations[0] in ["L", "R", "N"]:
                return [
                    TransitionRule(
                        rule.m_config,
                        rule.symbols,
                        [rule.symbols, operations[0]],
                        rule.next_m_config,
                    )
                ]
            else:
                return [
                    TransitionRule(
                        rule.m_config,
                        rule.symbols,
                        [operations[0], "N"],
                        rule.next_m_config,
                    )
                ]
        elif operations[0] not in ["L", "R", "N"] and operations[1] in [
            "L",
            "R",
            "N",
        ]:
            if len(operations) == 2:
                return [
                    TransitionRule(
                        rule.m_config,
                        rule.symbols,
                        operations[:2],
                        rule.next_m_config,
                    )
                ]

            self.q_cnt += 1
            new_m_config = f"q{self.q_cnt + 1}"
            first_rule = TransitionRule(
                rule.m_config, rule.symbols, operations[:2], new_m_config
            )
            seconds = []
            for symbol in self.vocab:
                seconds.append(
                    TransitionRule(
                        new_m_config,
                        symbol,
                        operations[2:],
                        rule.next_m_config,
                    )
                )
            return [first_rule] + sum(
                [self.expand_operations(r) for r in seconds], []
            )
        elif operations[0] not in ["L", "R", "N"]:
            self.q_cnt += 1
            new_m_config = f"q{self.q_cnt + 1}"
            first_rule = TransitionRule(
                rule.m_config, rule.symbols, [operations[0], "N"], new_m_config
            )
            seconds = []
            for symbol in self.vocab:
                seconds.append(
                    TransitionRule(
                        new_m_config,
                        symbol,
                        operations[1:],
                        rule.next_m_config,
                    )
                )
            return [first_rule] + sum(
                [self.expand_operations(r) for r in seconds], []
            )

        else:  # operations[0] in ["L", "R", "N"]:
            self.q_cnt += 1
            new_m_config = f"q{self.q_cnt + 1}"
            first_rule = TransitionRule(
                rule.m_config,
                rule.symbols,
                [operations[0]],
                new_m_config,
            )
            seconds = []
            for symbol in self.vocab:
                seconds.append(
                    TransitionRule(
                        new_m_config,
                        symbol,
                        operations[1:],
                        rule.next_m_config,
                    )
                )
            return self.expand_operations(first_rule) + sum(
                [self.expand_operations(r) for r in seconds], []
            )

    def encode_rule_to_5_tuple(self, table: Table):
        """
        Encode the transition rule into 5-tuple description
        e.g. (b, "_", ["$", "R", "$", "R", ], "c") -> (b, None, 0, R, c)
        """
        new_table = Table()
        for rule in table.rules:
            rules = self.expand_operations(rule)
            for r in rules:
                new_table.add_rule(r)

        return new_table

    @property
    def standard_form(self):
        codes = []
        for rule in self.std_form_table.rules:
            m_config, symbol, operations, next_m_config = rule
            print, move = operations
            codes.append(f"{m_config}{symbol}{print}{move}{next_m_config};")
        return "".join(codes)

    @property
    def standard_description(self):
        """
        Encode the transition table into standard description
        """
        codes = []
        for rule in self.std_form_table.rules:
            m_config, symbol, operations, next_m_config = rule
            codes.append(self.encode_m_config(m_config))
            codes.append(self.encode_symbol(symbol))
            codes.append(self.encode_operations(operations))
            codes.append(self.encode_m_config(next_m_config))
            codes.append(";")
        return "".join(codes)

    @property
    def description_number(self):
        """
        Encode the transition table into the description number
        """
        code_map = {"A": 1, "C": 2, "D": 3, "L": 4, "R": 5, "N": 6, ";": 7}
        code = []
        std_desc = self.standard_description
        for c in std_desc:
            code.append(str(code_map[c]))
        return "".join(code)

    def encode_m_config(self, m_config: str):
        number = int(m_config[1:])
        return "D" + "A" * number

    def encode_symbol(self, symbol: str):
        return self.std_map[symbol]

    def encode_operations(self, operations: list):
        assert (
            len(operations) == 2
        ), "The operations should be a pair of operations"
        print, move = operations
        assert move in [
            "L",
            "R",
            "N",
        ], "The move operation should be L, R, or N"
        assert (
            print in self.vocab
        ), "The print operation should be in the vocabulary"
        return self.std_map[print] + move


# Test Cases


def test_max_m_config_number():
    from pprint import pprint

    pprint("test find the right most x")

    SkelotonCompiler.reset()
    e = EraseAllMark("success")
    table = SkelotonCompiler.compile()

    encoder = Encoder(table, {"0", "1"}, {"_", "x"})
    pprint(table.table)
    pprint(encoder.q_cnt)


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


def test_expand_operations():
    from pprint import pprint

    pprint("test_expand_operations ")

    SkelotonCompiler.reset()
    table = SkelotonCompiler.compile()
    rule = TransitionRule("b", "_", ["$", "R", "$", "R"], "c")

    encoder = Encoder(table, {"0", "1", "$"}, {"_", "x"})
    pprint(encoder.expand_operations(rule))
    rule = TransitionRule("b", "_", ["$", "R", "$"], "c")
    pprint(encoder.expand_operations(rule))
    rule = TransitionRule("b", "_", ["$"], "c")
    pprint(encoder.expand_operations(rule))
    rule = TransitionRule(
        "b", "_", ["$", "R", "$", "R", "0", "R", "R", "0", "L", "L"], "o"
    )  # exponential expansion, so it's not recommended to write a rule with too many operations
    pprint(len(encoder.expand_operations(rule)))


def test_std_form_table_standard_encoding():
    from pprint import pprint

    pprint("test_std_form_table ")

    SkelotonCompiler.reset()
    e = FindRight("success", "x")
    table = SkelotonCompiler.compile()
    table.add_rule(TransitionRule("b", "_", ["$", "R", "$", "R"], "c"))
    table.add_rule(
        TransitionRule("c", "_", [], SkelotonCompiler.get_m_config_name(e))
    )

    encoder = Encoder(table, {"0", "1", "$"}, {"_", "x"})
    pprint("origin table:")
    pprint(encoder.origin_table)
    pprint("symbol expanded table:")
    pprint(encoder.symbol_expanded_table)
    pprint("m_config std table:")
    pprint(encoder.m_config_std_table)
    pprint("std form table:")
    pprint(encoder.std_form_table)
    pprint(encoder.standard_form)
    pprint(encoder.standard_description)
    pprint(encoder.description_number)


if __name__ == "__main__":
    test_max_m_config_number()
    test_expand_any_regex_symbol()
    test_symbol_from_current_head()
    test_m_config_name_normalize()
    test_expand_operations()
    test_std_form_table_standard_encoding()
