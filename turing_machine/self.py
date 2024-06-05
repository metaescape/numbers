"""
A Scratch file for testing the quine turing machine (not fully implemented)
"""

try:
    from turing_machine.op_extend import Table, TransitionRule, TuringMachine
    from turing_machine.abbreviated import (
        SkelotonCompiler,
        AbbreviatedTable,
    )
    from turing_machine.encoding import Assembler
except:
    from op_extend import Table, TransitionRule, TuringMachine
    from abbreviated import (
        SkelotonCompiler,
        AbbreviatedTable,
    )
    from encoding import Assembler

import re

SELF_VOCAB = [
    "R",
    "L",
    "_",
    "*",
    "A",
    "C",
    "D",
    "N",
    "P",
    "$",
    "x",
    "y",
]


class SelfEncoderDecoder(Assembler):
    def __init__(self, table: Table, vocab=SELF_VOCAB):
        """
        Do not extend `*` symbol and do not convert the table to 5-tuple form.
        """
        self.origin_table = table
        self.vocab = vocab
        self.build_symbol_map()

        self.q_cnt = self.get_max_m_config_number()
        self.m_config_std_table = self.standardize_m_configuration(table.table)

    def build_symbol_map(self):
        self.symbol2code = {}
        self.code2symbol = {}
        cnt = 0
        for symbol in self.vocab:
            if symbol not in self.symbol2code:
                self.symbol2code[symbol] = "D" + cnt * "C"
                self.code2symbol[self.symbol2code[symbol]] = symbol
                cnt += 1
        self.std_map = self.symbol2code

    def encode_rule(self, rule: TransitionRule, verbose=False):
        m_config, symbols, operations, next_m_config = rule
        assert len(symbols) == 1, "Only support single symbol transition rule"
        result = []
        m_config_code = self.encode_m_config(m_config)
        result.append(m_config_code)
        if verbose:
            print(f"map: {m_config} -> {m_config_code}")
        symbol_code = self.std_map[symbols]
        result.append(symbol_code)
        if verbose:
            print(f"map: {symbols} -> {symbol_code}")

        for op in operations:
            op_code = self.std_map[op]
            result.append(op_code)
            if verbose:
                print(f"map: {op} -> {op_code}")

        next_m_config_code = self.encode_m_config(next_m_config)
        result.append(next_m_config_code)
        if verbose:
            print(f"map: {next_m_config} -> {next_m_config_code}")

        return "".join(result)

    def decode_rule(self, code: str):
        """
        all symbols on the tape are in {D,A,_}
        """

        pattern = r"(DA+)|(DC*)"

        # Find all matches according to the pattern
        matches = re.findall(pattern, code)

        # Post-process to combine the tuple results into a single list
        result = ["".join(match) for match in matches]
        m_config_code, symbol_code, *operations_code, next_m_config_code = (
            result
        )
        m_config = f"q{len(m_config_code) - 1}"
        symbol = self.code2symbol[symbol_code]
        operations = []
        for op_code in operations_code:
            operations.append(self.code2symbol[op_code])
        next_m_config = f"q{len(next_m_config_code)-1}"
        rule = TransitionRule(m_config, symbol, operations, next_m_config)
        return rule

    def encode_table(self):
        result = []
        for rule in self.m_config_std_table.rules:
            result.append(self.encode_rule(rule))

        return "".join(result)

    def encode_to_print_inst(self, code):
        """DADCCCCCCCCCDDAA will translate to PAPCCCCCCCCCPPAA"""
        return code.replace("D", "P")

    def decode_tape_str_to_table(self, code: str):
        if "PA" in code:
            code = code.replace("P", "D")
            return self.generate_a_part(code)
        else:
            return self.decode_DADC_to_table(code)

    def decode_DADC_to_table(self, code: str):
        pattern = r"(DA+)|(DC*)"

        # Find all matches according to the pattern
        matches = re.findall(pattern, code)

        result = ["".join(match) for match in matches]
        table = Table()
        i, j = 0, 1
        while j < len(result):
            while j < len(result) and "DA" not in result[j]:
                j += 1
            table.add_rule(self.decode_rule("".join(result[i : j + 1])))

            i = j + 1
            j += 2

        return table

    def generate_a_part(self, code: str):
        operations = ["$", "R", "$", "R"]
        for c in code:
            operations.append(c)
            operations.append("R")
            operations.append("R")

        rule = TransitionRule("q10", "_", operations, "q1")
        table = Table()
        table.add_rule(rule)
        return table


def print_my_self():
    with open(__file__, "r") as f:
        lines = f.read()
        print(lines)


class ForwardSearch(AbbreviatedTable):
    def __init__(self, success):
        super().__init__()


class PartB_(AbbreviatedTable):
    def __init__(self, success):
        super().__init__()
        self.add_transition("$", ["R"], PrintInst(success, "_"))


class PrintInst(AbbreviatedTable):
    def __init__(self, success, alpha):
        super().__init__()
        self.add_transition("$", [], FindFirstMark1(success, alpha))
        self.add_transition("*", ["L"], self)


class FindFirstMark1(AbbreviatedTable):
    def __init__(self, success, alpha):
        super().__init__()
        self.add_transition(alpha, ["x", "L"], FindFirstMark2(success))
        self.add_transition("*", ["R", "R"], self)


class FindFirstMark2(AbbreviatedTable):
    def __init__(self, success):
        super().__init__()
        self.add_transition("D", [], Copy2End(success, "P"))
        self.add_transition("A", [], Copy2End(success, "A"))
        self.add_transition("C", [], Copy2End(success, "C"))
        self.add_transition("_", ["R"], EraseBack(success))


class Copy2End(AbbreviatedTable):
    def __init__(self, success, alpha):
        super().__init__()
        self.add_transition("_", [alpha, "R", "y"], PrintInst(success, "_"))
        self.add_transition("*", ["R", "R"], self)


class EraseBack(AbbreviatedTable):
    def __init__(self, success):
        super().__init__()
        self.add_transition("$", [], success)
        self.add_transition("*", ["_", "L", "L"], self)


def test_part_b_machine():
    SkelotonCompiler.reset()
    SkelotonCompiler.set_vocab(SELF_VOCAB)
    b = PartB_("success")
    table = SkelotonCompiler.compile()

    encoder = SelfEncoderDecoder(table)
    print(encoder.encode_table())

    a_part = encoder.encode_to_print_inst(encoder.encode_table())
    print(a_part)

    decoded_table = encoder.decode_tape_str_to_table(encoder.encode_table())
    print(decoded_table)
    assert encoder.m_config_std_table == decoded_table
    print(encoder.decode_tape_str_to_table(a_part))


def test_encode_decode_rule():
    encoder = SelfEncoderDecoder(SkelotonCompiler.compile())
    rule = TransitionRule("q1", "A", ["R"], "q2")
    print(encoder.encode_rule(rule, True))
    rule = TransitionRule("q2", "*", ["R", "R", "P"], "q8")
    encoded = encoder.encode_rule(rule, True)
    print(encoded)
    print(encoder.decode_rule(encoded))


def test_compile_copy_erase():
    from pprint import pprint

    pprint("test copy marked and erase x")

    SkelotonCompiler.reset()
    SkelotonCompiler.set_vocab(SELF_VOCAB)
    b = PartB_("success")
    table = SkelotonCompiler.compile()

    encoder = SelfEncoderDecoder(table)

    rule = TransitionRule("q1", "*", ["R", "R", "_"], "q2")
    encoded = encoder.encode_rule(rule, True)

    pprint(table.table)
    tm = TuringMachine(table, SkelotonCompiler.get_m_config_name(b))
    tm.set_figures(encoded)
    total = 1022
    tm.run(steps=total, verbose=range(total - 50, total))

    return tm


def test_self_print_machine():
    import copy

    SkelotonCompiler.reset()
    SkelotonCompiler.set_vocab(SELF_VOCAB)
    b = PrintInst("success", "_")
    table = SkelotonCompiler.compile()

    encoder = SelfEncoderDecoder(table)
    a_part_str = encoder.encode_to_print_inst(encoder.encode_table())
    a_part = encoder.decode_tape_str_to_table(a_part_str)
    b_part = encoder.m_config_std_table
    ab_self_print = copy.deepcopy(b_part)
    ab_self_print.merge(a_part)
    # print(ab_self_print)
    tm = TuringMachine(ab_self_print, "q10")
    total = 1000
    tm.run(steps=total, verbose=range(total - 50, total))


# 调用函数
if __name__ == "__main__":
    # print_my_self()
    test_encode_decode_rule()
    test_compile_copy_erase()
    test_part_b_machine()
    test_self_print_machine()
