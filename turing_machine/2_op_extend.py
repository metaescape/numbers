"""
Simulate a Turing machine , the length operation in transiction rule is variable

support two directions: "L" and "R", Writing symbol support "e", "x", "0", "1", None(erase)

support match any symbol with "*"

also with pretty print fro complete configuration
"""


class TuringMachine:
    """
    This is a Turing machine interpreter, not a universal Turing machine.
    """

    def __init__(self, table, initial_state):
        self.tape = [None] * 2000
        self.head_position = 0
        self.table = table
        self.current_state = initial_state
        self.max_right = 0
        self.history = []
        self.fill_len = 3

    def set_fill_len(self, fill_len):
        self.fill_len = fill_len

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

    def get_tape(self):
        """
        point: left or bracket
        """
        tape = self.tape[: self.max_right + 1]
        return [ele if ele else "_" for ele in tape]

    def str(self, turing=False):
        tape = self.get_tape()
        m_config = self.m_configuration
        if turing:
            left = "".join(tape[: self.head_position])
            right = "".join(tape[self.head_position :])
            return f":{left}{self.m_configuration}{right}"
        else:
            tape[self.head_position] = f"[{tape[self.head_position]}]"
            s = "".join(tape)
            return f"{m_config:>{self.fill_len}} | {s}"

    def get_sequence(self):
        result = []
        for i in range(0, len(self.tape), 2):
            if self.tape[i] in ("0", "1"):
                result.append(self.tape[i])
        return "".join(result)

    def get_binary(self):
        return "0." + self.get_sequence()

    def get_history(self):
        return "".join(self.history) + ":"

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
                        self.tape.extend([None] * 2000)
                        print(
                            f"Warning: head position is out of tape,"
                            f"extend tape from length {length_before} to {len(self.tape)}"
                        )
                elif operation == "L":
                    self.head_position -= 1
                    if self.head_position < 0:
                        print("Warning: head position is negative, reset to 0")
                        self.head_position = 0

                else:
                    write_symbol = operation
                    self.tape[self.head_position] = write_symbol

            self.current_state = next_m_config
            self.history.append(self.str(turing=True))
            if verbose:
                print(f"{idx + 1}: {self.str(turing=False)}")

        else:
            raise Exception(
                f"No transition defined for the current configuration {configuration}"
            )

    def run(self, steps=1000, verbose=False):
        """运行图灵机直到达到终止状态"""
        for i in range(steps):
            self.step(i, verbose=verbose)


class TransitionRule:

    def __init__(self, m_config, symbol, operations: list, next_m_config):
        """
        m_config: 当前状态
        symbol: 当前读取的符号, 如果是 *, 表示任意符号
        operations: 操作列表，包括写入的符号、方向
        next_m_config: 下一个状态

        """
        self.m_config = m_config
        self.symbol = symbol
        self.operations = operations
        self.next_m_config = next_m_config

    def configuration(self):
        return (self.m_config, self.symbol)

    def behavior(self):
        return self.operations, self.next_m_config


class Table:
    """
    support match any symbol
    """

    def __init__(self):
        self.table = {}

    def __contains__(self, key):
        m_config, symbol = key
        if m_config in self.table and symbol:
            # match any symbol
            return True
        return key in self.table

    def __getitem__(self, key):
        m_config, symbol = key
        if m_config in self.table and symbol:
            return self.table[m_config]
        return self.table[key]

    def add_rule(self, rule: TransitionRule):
        m_config, symbol = rule.configuration()
        value = rule.behavior()
        if symbol == "*":
            self.table[m_config] = value
        else:
            self.table[(m_config, symbol)] = value


def test_1_3_machine():
    """
    The variation of first example from Turing Paper 1936, this is the description of a turing machine
    """
    bcek_table = Table()

    bcek_table.add_rule(TransitionRule("b", None, ["0"], "b"))
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
        ("b", None, ["e", "R", "e", "R", "0", "R", "R", "0", "L", "L"], "o"),
        ("o", "1", ["R", "x", "L", "L", "L"], "o"),
        ("o", "0", [], "q"),
        ("q", "*", ["R", "R"], "q"),
        ("q", None, ["1", "L"], "p"),
        ("p", "x", [None, "R"], "q"),
        ("p", "e", ["R"], "f"),
        ("p", None, ["L", "L"], "p"),
        ("f", "*", ["R", "R"], "f"),
        ("f", None, ["0", "L", "L"], "o"),
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
        ("begin", None, ["e", "R", "R", "0"], "increment"),
        ("increment", "0", ["1"], "2left"),
        ("increment", "1", ["0", "R", "R"], "increment"),
        ("increment", None, ["1"], "2left"),
        ("2left", "0", ["L", "L"], "2left"),
        ("2left", "1", ["L", "L"], "2left"),
        ("2left", "e", ["R", "R"], "increment"),
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


if __name__ == "__main__":
    test_1_3_machine()

    test_transcendental_machine()
    test_increment_machine()
