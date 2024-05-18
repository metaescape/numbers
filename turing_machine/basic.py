"""
Simulate a Basic Turing machine

the  operations length is 2, the first element is the symbol to write, the second element is the direction to move

only support two directions: "L" and "R"
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
    def complete_configuration(self):
        return (self.tape, self.head_position, self.m_configuration)

    def get_tape(self):
        return self.tape

    def get_sequence(self):
        result = []
        for i in range(0, len(self.tape), 2):
            if self.tape[i] in ("0", "1"):
                result.append(self.tape[i])
        return "".join(result)

    def get_binary(self):
        return "0." + self.get_sequence()

    def get_decimal(self):
        """
        convert 0.01010101... to 1/3 in decimal
        """
        sequence = self.get_sequence()
        result = 0
        for i in range(len(sequence)):
            result += int(sequence[i]) * 2 ** (-i - 1)
        return result

    def step(self):
        """执行图灵机的单步操作"""
        configuration = self.configuration

        print(configuration)
        if configuration in self.table:
            operations, next_m_config = self.table[configuration]
            write_symbol, move = operations
            if write_symbol:
                self.tape[self.head_position] = write_symbol
            if move == "R":
                self.head_position += 1
                if self.head_position >= len(self.tape):
                    length_before = len(self.tape)
                    self.tape.extend([None] * 2000)
                    print(
                        f"Warning: head position is out of tape,"
                        f"extend tape from length {length_before} to {len(self.tape)}"
                    )
            elif move == "L":
                self.head_position -= 1
            if self.head_position < 0:
                print("Warning: head position is negative, reset to 0")
                self.head_position = 0
            self.current_state = next_m_config

        else:
            raise Exception(
                "No transition defined for the current configuration"
            )

    def run(self, steps=1000):
        """运行图灵机直到达到终止状态"""
        for _ in range(steps):
            self.step()


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
    def __init__(self):
        self.table = {}

    def __contains__(self, key):
        return key in self.table

    def __getitem__(self, key):
        return self.table[key]

    def add_rule(self, rule: TransitionRule):
        key = rule.configuration()
        value = rule.behavior()
        self.table[key] = value


def create_1_3_table():
    """
    The first example from Turing Paper 1936, this is the description of a turing machine
    """
    bcek_table = Table()

    bcek_table.add_rule(TransitionRule("b", None, ["0", "R"], "c"))
    bcek_table.add_rule(TransitionRule("c", None, [None, "R"], "e"))
    bcek_table.add_rule(TransitionRule("e", None, ["1", "R"], "k"))
    bcek_table.add_rule(TransitionRule("k", None, [None, "R"], "b"))

    return bcek_table


def create_1_4_table():
    """
    The first example from Turing Paper 1936, this is the description of a turing machine
    """
    bcdef_table = Table()

    bcdef_table.add_rule(TransitionRule("b", None, ["0", "R"], "c"))
    bcdef_table.add_rule(TransitionRule("c", None, [None, "R"], "d"))
    bcdef_table.add_rule(TransitionRule("d", None, ["1", "R"], "e"))
    bcdef_table.add_rule(TransitionRule("e", None, [None, "R"], "f"))
    bcdef_table.add_rule(TransitionRule("f", None, ["0", "R"], "e"))

    return bcdef_table


if __name__ == "__main__":

    tm = TuringMachine(create_1_3_table(), "b")
    tm.run(steps=20)
    print(tm.get_sequence())
    print(tm.get_decimal())

    tm = TuringMachine(create_1_4_table(), "b")
    tm.run(steps=20)
    print(tm.get_sequence())
    print(tm.get_decimal())
