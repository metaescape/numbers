"""
This script reproduces the 0 translator in Chapter 9 "Application of the diagonal process" from Turing's 1936 paper.

The 0 translator takes a description of a Turing machine M as input and produces a description of 
a Turing machine M' that is equivalent to M except that the first 0 printed by M is replaced by "-".


Author: Metaesc
Email: metaescape@foxmail.com
License: MIT License
"""

try:
    from turing_machine.op_extend import (
        Table,
        TransitionRule,
        TuringMachine,
        create_sqrt2_table,
    )
except:
    from op_extend import (
        Table,
        TransitionRule,
        TuringMachine,
        create_sqrt2_table,
    )


def traslator0(machine: Table):
    """
    The 0 translator takes a Table of a Turing machine M as input and produces a new table of
    a Turing machine M' that is equivalent to M except that the first 0 printed by M is replaced by "-".

    """

    m_config_map = {}
    max_q = 0
    for rule in machine.rules:
        m_config = rule.m_config
        m_config_map[m_config] = None
        if m_config.startswith("q"):
            number = int(m_config[1:])
            max_q = max(max_q, number)

    print(f"there are {len(m_config_map)} m-configs in the machine")
    # create m-config map
    for m_config in m_config_map:
        max_q += 1
        m_config_map[m_config] = f"q{max_q}"

    new_transition_rules = []
    for rule in machine.rules:
        m_config, symbols, operations, next_m_config = rule
        new_m_config = m_config_map[m_config]
        new_next_m_config = m_config_map[next_m_config]

        new_operations = []
        first = True
        for operation in operations:
            if operation == "0" and first:
                new_operations.append("-")
                first = False
            else:
                new_operations.append(operation)
        if not first:
            rewrite = TransitionRule(
                m_config, symbols, new_operations, new_next_m_config
            )
            new_transition_rules.append(rewrite)
        else:
            new_transition_rules.append(rule)

        new_rule = TransitionRule(
            new_m_config, symbols, operations, new_next_m_config
        )
        new_transition_rules.append(new_rule)

        if "0" in rule.symbols:
            new_rule = TransitionRule(
                new_m_config, "-", operations, new_next_m_config
            )
            new_transition_rules.append(new_rule)

    new_table = Table()
    for rule in new_transition_rules:
        new_table.add_rule(rule)
    return new_table


def test_1_3_machine_rewrite():
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
    origin_seq = tm.get_sequence()

    new_table = traslator0(bcek_table)
    new_tm = TuringMachine(new_table, "b")
    print(new_table)
    print("run 0 translator")
    new_tm.run(steps=20)
    new_seq = new_tm.get_sequence()
    print(origin_seq)
    print(new_seq)
    assert origin_seq[0] == "0" and new_seq[0] == "-"
    assert origin_seq[1:] == new_seq[1:]


def test_sqrt2_macine_rewrite():
    table = create_sqrt2_table()
    tm = TuringMachine(table, "begin")
    print("run sqrt2 machine")
    tm.run(steps=10000)
    origin_seq = tm.get_sequence()

    new_table = traslator0(table)
    new_tm = TuringMachine(new_table, "begin")
    print("run sqrt2 machine after 0 translator")
    new_tm.run(steps=10000)

    new_seq = new_tm.get_sequence()
    print(origin_seq)
    print(new_seq)
    assert origin_seq[1] == "0" and new_seq[1] == "-"
    assert origin_seq[2:] == new_seq[2:]


if __name__ == "__main__":
    test_1_3_machine_rewrite()
    test_sqrt2_macine_rewrite()
