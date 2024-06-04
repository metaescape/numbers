"""
This is almost the reproduction of chapter 3 "Examples of computing machines" in the Turing's 1936 paper. 

Features: 

- Support "*" in scanned symbol, which means match any symbol;

- The length of operations in the transition rules is variable;

- Action: "L" , "R" and "N" (no move);

- Writing symbols:  "$"(start), "x", "0", "1", "_"(erase or None) or any other symbols;

- pretty print for complete configuration


Author: Metaesc
Email: metaescape@foxmail.com
License: MIT License
"""


class TuringMachine:
    """
    This is a Turing machine interpreter, not a universal Turing machine.
    """

    def __init__(self, table, initial_state):
        self.tape = ["_"] * 2000
        self.head_position = 0
        self.table = table
        self.current_state = initial_state
        self.max_right = 0
        self.history = []
        self.fill_len = 3

    @property
    def m_configuration(self):
        return self.current_state

    @property
    def scanned_symbol(self):
        return (
            self.tape[self.head_position]
            if self.head_position < len(self.tape)
            else " "
        )

    @property
    def configuration(self):
        return (self.m_configuration, self.scanned_symbol)

    @property
    def complete_configuration(self, turing=False):
        """
        turing: use the same format in Turing's paper
        """
        return (self.m_configuration, self.get_tape())

    def set_tape(self, tape):
        n = len(tape)
        if n > len(self.tape):
            self.tape.extend(["_"] * (n - len(self.tape)))
        self.tape[:n] = tape
        self.max_right = len(tape)

    def get_tape(self):
        """
        point: left or bracket
        """
        tape = self.tape[: self.max_right + 1]
        return tape

    def set_fill_len(self, fill_len):
        """length for aligning m_configuration when print"""
        self.fill_len = fill_len

    def str(self, turing=False):
        tape = self.get_tape()
        m_config = self.m_configuration
        if turing:
            left = tape[: self.head_position]
            right = tape[self.head_position :]
            return left + [self.m_configuration] + right
        else:
            tape[self.head_position] = f"[{tape[self.head_position]}]"
            s = "".join(tape)
            return f"{m_config:>{self.fill_len}} | {s}"

    def get_sequence(self):
        result = []
        for i in range(0, self.max_right + 1, 2):
            if self.tape[i] not in {
                "$",
                "_",
            }:
                result.append(self.tape[i])
        return "".join(result)

    def get_binary(self):
        seq = self.get_sequence()
        if set(seq) == {"0", "1"}:
            return "0." + seq
        else:
            raise Exception(f"sequence is not binary: {seq}")

    def get_history(self):
        return (
            "".join(
                [
                    ":" + "".join(complete_config)
                    for complete_config in self.history
                ]
            )
            + ":"
        )

    def get_decimal(self):
        """
        convert 0.01010101... to 1/3 in decimal
        """
        sequence = self.get_sequence()
        result = 0
        for i in range(len(sequence)):
            result += int(sequence[i]) * 2 ** (-i - 1)
        return result

    def step(self, idx, verbose):
        """执行图灵机的单步操作"""
        configuration = self.configuration

        if configuration in self.table:
            operations, next_m_config = self.table[configuration]
            for operation in operations:
                if operation == "R":
                    self.head_position += 1
                    self.max_right = max(self.head_position, self.max_right)
                    if self.head_position >= len(self.tape):
                        length_before = len(self.tape)
                        self.tape.extend(["_"] * len(self.tape))
                        print(
                            f"Warning: head position is out of tape,"
                            f"extend tape from length {length_before} to {len(self.tape)}"
                        )
                elif operation == "L":
                    self.head_position -= 1
                    if self.head_position < 0:
                        print("Warning: head position is negative, reset to 0")
                        self.head_position = 0

                elif operation != "N":
                    write_symbol = operation

                    self.tape[self.head_position] = write_symbol

            self.current_state = next_m_config
            self.history.append(self.str(turing=True))
            if verbose == True or (verbose and idx in verbose):
                print(f"{idx + 1}: {self.str(turing=False)}")

        else:
            raise Exception(
                f"No transition defined for the current configuration {configuration}"
            )

    def run(self, steps=1000, verbose=False):
        """运行图灵机直到达到终止状态"""
        for i in range(steps):
            self.step(i, verbose=verbose)

    def load_instruction(self, code):
        """
        for universal turing machine
        """
        vocab = set(code)
        assert vocab.issubset({"R", "L", "N", ";", "D", "A", "C"})
        length = len(code) * 2 * 2
        if length > len(self.tape):
            self.tape = ["_"] * length
        self.tape[:2] = ["$", "$"]
        for i in range(len(code)):
            self.tape[2 + i * 2] = code[i]
        self.tape[2 + len(code) * 2] = "::"
        self.max_right = 2 + len(code) * 2


class TransitionRule:

    def __init__(
        self, m_config: str, symbols, operations: list, next_m_config
    ):
        """
        m_config: current state/m-configuration
        symbol: current symbol in the machine/under the reader, * match all symbols
        operations: R,L or symbol to write, "_" stands for erase/blanks
        next_m_config: next state/m-configuration

        """
        self.m_config = m_config
        self.symbols = symbols
        self.operations = operations
        self.next_m_config = next_m_config

    def configuration(self):
        return (self.m_config, self.symbols)

    def behavior(self):
        return self.operations, self.next_m_config

    def __repr__(self):
        return f"{self.m_config} {self.symbols} -> {self.operations} {self.next_m_config}"

    def __iter__(self):
        yield self.m_config
        yield self.symbols
        yield self.operations
        yield self.next_m_config


class Table:
    """
    support match any symbol
    """

    def __init__(self):
        self.table = {}
        self.rules = []

    def __contains__(self, key):
        m_config, _ = key
        if key in self.table:
            return True
        return (m_config, "*") in self.table

    def __getitem__(self, key):
        m_config, _ = key
        if key in self.table:
            return self.table[key]
        return self.table[(m_config, "*")]

    def add_rule(self, rule: TransitionRule):
        self.rules.append(rule)
        m_config, symbols = rule.configuration()
        value = rule.behavior()
        symbols = [symbols] if not symbols else symbols
        if "*" in symbols:
            assert symbols[-1] == "*", "* shold not be in last position"
        if "::" in symbols:
            assert (
                len(symbols) == 2
            ), " :: is a specical length two symbol,make sure only :: in it"
            self.table[(m_config, "::")] = value
        else:
            for symbol in symbols:
                self.table[(m_config, symbol)] = value

    def __repr__(self):
        return "\n".join([str(rule) for rule in self.rules])


def test_1_3_machine():
    """
    The variation of first example from Turing Paper 1936, this is the description of a turing machine
    """
    bcek_table = Table()

    bcek_table.add_rule(TransitionRule("b", "_", ["0"], "b"))
    bcek_table.add_rule(TransitionRule("b", "0", ["R", "R", "1"], "b"))
    bcek_table.add_rule(TransitionRule("b", "1", ["R", "R", "0"], "b"))

    tm = TuringMachine(bcek_table, "b")
    print("run 1/3 turing machine")
    tm.run(steps=20)
    print(tm.get_sequence())
    print(tm.get_decimal())


def test_transcendental_machine():
    """
    Turing machine for print 001011011101111...
    The second example from Turing Paper 1936
    """

    table = Table()
    description = [
        ("b", "_", ["$", "R", "$", "R", "0", "R", "R", "0", "L", "L"], "o"),
        ("o", "1", ["R", "x", "L", "L", "L"], "o"),
        ("o", "0", [], "q"),
        ("q", "*", ["R", "R"], "q"),
        ("q", "_", ["1", "L"], "p"),
        ("p", "x", ["_", "R"], "q"),
        ("p", "$", ["R"], "f"),
        ("p", "_", ["L", "L"], "p"),
        ("f", "*", ["R", "R"], "f"),
        ("f", "_", ["0", "L", "L"], "o"),
    ]
    for rule in description:
        table.add_rule(TransitionRule(*rule))

    tm = TuringMachine(table, "b")
    print("run transcendental turing machine")
    tm.run(steps=80, verbose=True)
    print(tm.get_sequence())
    print(tm.get_decimal())
    print(tm.get_history())


def test_increment_machine():
    """
    Turing machine for increment binary number
    """
    table = Table()
    description = [
        ("begin", "_", ["$", "R", "R", "0"], "increment"),
        ("increment", "0", ["1"], "2left"),
        ("increment", "1", ["0", "R", "R"], "increment"),
        ("increment", "_", ["1"], "2left"),
        ("2left", "01", ["L", "L"], "2left"),
        ("2left", "$", ["R", "R"], "increment"),
    ]
    for rule in description:
        table.add_rule(TransitionRule(*rule))

    print("run transcendental turing machine")
    for steps in range(1, 40):
        tm = TuringMachine(table, "begin")
        tm.fill_len = 10

        tm.run(steps=steps)

        # reverse the sequence
        print(int(tm.get_sequence()[::-1], 2))


def create_sqrt2_table():
    table = Table()
    description = [
        ("begin", "_", ["$", "R", "$", "R", "1"], "new"),
        ("new", "$", ["R"], "mark-digits"),
        ("new", "*", ["L"], "new"),
        ("mark-digits", "01", ["R", "x", "R"], "mark-digits"),
        ("mark-digits", "_", ["R", "z", "R", "R", "r"], "find-x"),
        ("find-x", "x", ["_"], "first-r"),
        ("find-x", "$", [], "find-digits"),
        ("find-x", "*", ["L", "L"], "find-x"),
        ("first-r", "r", ["R", "R"], "last-r"),
        ("first-r", "*", ["R", "R"], "first-r"),
        ("last-r", "r", ["R", "R"], "last-r"),
        ("last-r", "_", ["r", "R", "R", "r"], "find-x"),
        ("find-digits", "$", ["R", "R"], "find-1st-digit"),
        ("find-digits", "*", ["L", "L"], "find-digits"),
        ("find-1st-digit", "xy", ["L"], "found-1st-digit"),
        ("find-1st-digit", "z", ["L"], "found-2nd-digit"),
        ("find-1st-digit", "_", ["R", "R"], "find-1st-digit"),
        ("found-1st-digit", "0", ["R"], "add-zero"),
        ("found-1st-digit", "1", ["R", "R", "R"], "find-2nd-digit"),
        ("find-2nd-digit", "xy", ["L"], "found-2nd-digit"),
        ("find-2nd-digit", "_", ["R", "R"], "find-2nd-digit"),
        ("found-2nd-digit", "0", ["R"], "add-zero"),
        ("found-2nd-digit", "1_", ["R"], "add-one"),
        ("add-zero", "r", ["s"], "add-finished"),
        ("add-zero", "u", ["v"], "add-finished"),
        ("add-zero", "*", ["R", "R"], "add-zero"),
        ("add-one", "r", ["v"], "add-finished"),
        ("add-one", "u", ["s", "R", "R"], "carry"),
        ("add-one", "*", ["R", "R"], "add-one"),
        ("carry", "r", ["u"], "add-finished"),
        ("carry", "_", ["u"], "new-digit-is-zero"),
        ("carry", "u", ["r", "R", "R"], "carry"),
        ("add-finished", "$", ["R", "R"], "erase-old-x"),
        ("add-finished", "*", ["L", "L"], "add-finished"),
        ("erase-old-x", "x", ["_", "L", "L"], "print-new-x"),
        ("erase-old-x", "z", ["y", "L", "L"], "print-new-x"),
        ("erase-old-x", "*", ["R", "R"], "erase-old-x"),
        ("print-new-x", "$", ["R", "R"], "erase-old-y"),
        ("print-new-x", "y", ["z"], "find-digits"),
        ("print-new-x", "_", ["x"], "find-digits"),
        ("erase-old-y", "y", ["_", "L", "L"], "print-new-y"),
        ("erase-old-y", "*", ["R", "R"], "erase-old-y"),
        ("print-new-y", "$", ["R"], "new-digit-is-one"),
        ("print-new-y", "*", ["y", "R"], "reset-new-x"),
        ("reset-new-x", "_", ["R", "x"], "flag-result-digits"),
        ("reset-new-x", "*", ["R", "R"], "reset-new-x"),
        ("flag-result-digits", "s", ["t", "R", "R"], "unflag-result-digits"),
        ("flag-result-digits", "v", ["w", "R", "R"], "unflag-result-digits"),
        ("flag-result-digits", "*", ["R", "R"], "flag-result-digits"),
        ("unflag-result-digits", "s", ["r", "R", "R"], "unflag-result-digits"),
        ("unflag-result-digits", "v", ["u", "R", "R"], "unflag-result-digits"),
        ("unflag-result-digits", "*", [], "find-digits"),
        ("new-digit-is-zero", "$", ["R"], "print-zero-digit"),
        ("new-digit-is-zero", "*", ["L"], "new-digit-is-zero"),
        ("print-zero-digit", "01", ["R", "_", "R"], "print-zero-digit"),
        ("print-zero-digit", "_", ["0", "R", "R", "R"], "cleanup"),
        ("new-digit-is-one", "$", ["R"], "print-one-digit"),
        ("new-digit-is-one", "*", ["L"], "new-digit-is-one"),
        ("print-one-digit", "01", ["R", "_", "R"], "print-one-digit"),
        ("print-one-digit", "_", ["1", "R", "R", "R"], "cleanup"),
        ("cleanup", "_", [], "new"),
        ("cleanup", "*", ["_", "R", "R"], "cleanup"),
    ]
    for rule in description:
        table.add_rule(TransitionRule(*rule))
    return table


def test_sqrt_root_machine():
    """
    Turing machine for find sqrt root, reproduce the example in chapter 6 of the book "Annoted Turing"
    """
    table = create_sqrt2_table()

    print("run sqrt(2) turing machine")

    tm = TuringMachine(table, "begin")
    tm.fill_len = 18
    tm.run(steps=10000, verbose=False)
    # tm.run(steps=400, verbose=True) # for debug
    print(tm.get_sequence())
    print(tm.get_decimal() * 2)


if __name__ == "__main__":
    test_1_3_machine()
    test_transcendental_machine()
    test_increment_machine()
    test_sqrt_root_machine()
