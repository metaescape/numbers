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

SELF_VOCAB = [
    "_",
    "$",
    "R",
    "L",
    "N",
    "D",
    "A",
    "C",
    "P",
    "*",
    "x",
    "y",
]


class SelfEncoderDecoder(Assembler):
    def __init__(self, table: Table, vocab: set = set(SELF_VOCAB)):
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
        import re

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


def print_my_self():
    with open(__file__, "r") as f:
        lines = f.read()
        print(lines)


def create_print_self_machine():
    pass


class ForwardSearch(AbbreviatedTable):
    def __init__(self, success):
        super().__init__()


class PartB(AbbreviatedTable):
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


class Copy2End(AbbreviatedTable):
    def __init__(self, success, alpha):
        super().__init__()
        self.add_transition("_", [alpha, "R", "y"], PrintInst(success, "_"))
        for char in SkelotonCompiler.vocab:
            if char != "_":
                self.add_transition(char, ["R", "R"], self)


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

    pprint("test copy xed and erase x")

    SkelotonCompiler.reset()
    SkelotonCompiler.set_vocab(SELF_VOCAB)
    b = PartB("success")
    table = SkelotonCompiler.compile()

    pprint(table.table)
    convert_to_code(table)
    tm = TuringMachine(table, SkelotonCompiler.get_m_config_name(b))
    tm.set_tape(["$", "$", "D", "_", "A"])
    tm.run(steps=50, verbose=True)
    print(tm.get_tape())

    return tm


def convert_to_code(table: Table):
    encoder = SelfEncoderDecoder(table)
    res = []
    # breakpoint()
    print(encoder.q_cnt)
    # print(encoder.std_form_table)
    # print(len(encoder.standard_description))  # buggy, need to add new coding


# 调用函数
if __name__ == "__main__":
    print_my_self()
    # test_compile_copy_erase()
    test_encode_decode_rule()
