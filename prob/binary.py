"""
structure Causal Model:
U = e_u ; e_u ~ Bernoulli(0.5)
A = int(e_a + U/4>=1) ; e_a ~ Unif(0, 1)
M = int(e_m + 10(1-A) <= 60) ; e_m ~ Unif(0, 100)
Y = int(e_y + M/2 + U/4 >= 1) ; e_y ~ Unif(0, 1)
"""


def bernoulli(value, p=0.5):
    assert value == 0 or value == 1
    return p**value * (1 - p) ** (1 - value)


def joint_prob(assignments):
    u, a, m, y = (
        assignments["U"],
        assignments["A"],
        assignments["M"],
        assignments["Y"],
    )
    return (
        bernoulli(u)
        * bernoulli(a, u / 4)
        * bernoulli(m, 0.5 + 0.1 * a)
        * bernoulli(y, m / 2 + u / 4)
    )


def intervention_prob_a1(assignments):
    """
    P(X|do(A=1))
    """
    u, a, m, y = (
        assignments["U"],
        assignments["A"],
        assignments["M"],
        assignments["Y"],
    )
    return (
        bernoulli(u)
        * bernoulli(a, 1)
        * bernoulli(m, 0.5 + 0.1)
        * bernoulli(y, m / 2 + u / 4)
    )


def intervention_prob_a0(assignments):
    """
    P(X|do(A=0))
    """
    u, a, m, y = (
        assignments["U"],
        assignments["A"],
        assignments["M"],
        assignments["Y"],
    )
    return (
        bernoulli(u)
        * bernoulli(a, 0)
        * bernoulli(m, 0.5)
        * bernoulli(y, m / 2 + u / 4)
    )


def print_joint_table(prob):
    for u in range(2):
        for a in range(2):
            for m in range(2):
                for y in range(2):
                    assignments = {"U": u, "A": a, "M": m, "Y": y}
                    print(u, a, m, y, prob(assignments))


def generate_all_assignments(vars):
    if len(vars) == 0:
        return [{}]
    else:
        var = vars[0]
        remains = vars[1:]
        assignments = []
        for value in range(2):
            for assignment in generate_all_assignments(remains):
                assignments.append({var: value, **assignment})
        return assignments


def conditional_prob(joint_prob, targets: dict, conditions: dict = {}):

    queries = {**targets, **conditions}

    remains1 = list(set(["U", "A", "M", "Y"]) - set(queries.keys()))

    numerator = 0
    for assignment in generate_all_assignments(remains1):
        numerator += joint_prob({**assignment, **queries})

    if len(conditions) == 0:
        return numerator

    remains2 = list(set(["U", "A", "M", "Y"]) - set(conditions.keys()))
    denominator = 0
    for assignment in generate_all_assignments(remains2):
        denominator += joint_prob({**assignment, **conditions})
    if denominator == 0:
        return 0.3  # only for P(Y = 1 | A = 1, U = 0)
    return numerator / denominator


if __name__ == "__main__":
    print_joint_table(joint_prob)
    # print(generate_all_assignments(["U", "A", "M", "Y"]))
    print("P(Y=1) =", conditional_prob(joint_prob, {"Y": 1}))
    print(
        "P(Y=1|M=0, A=0) =",
        conditional_prob(joint_prob, {"Y": 1}, {"M": 0, "A": 0}),
    )
    print(
        "P(Y=1|M=0, A=1) =",
        conditional_prob(joint_prob, {"Y": 1}, {"M": 0, "A": 1}),
    )

    print("P(Y=1|do(A=1)) =", conditional_prob(intervention_prob_a1, {"Y": 1}))

    # P(Y=1|do(A=0))
    print("P(Y=1|do(A=0)) =", conditional_prob(intervention_prob_a0, {"Y": 1}))

    # P(Y=0|do(A=1))
    print("P(Y=0|do(A=1)) =", conditional_prob(intervention_prob_a1, {"Y": 0}))

    # P(Y=0|do(A=0))
    print("P(Y=0|do(A=0)) =", conditional_prob(intervention_prob_a0, {"Y": 0}))
    print(
        "P(Y=1|A=0, U=0) =",
        conditional_prob(joint_prob, {"Y": 1}, {"U": 0, "A": 0}),
    )
    print(
        "P(Y=1|A=0, U=1) =",
        conditional_prob(joint_prob, {"Y": 1}, {"U": 1, "A": 0}),
    )
    print(
        "P(Y=1|A=1, U=0) =",
        conditional_prob(joint_prob, {"Y": 1}, {"U": 0, "A": 1}),
    )
    print(
        "P(Y=1|A=1, U=1) =",
        conditional_prob(joint_prob, {"Y": 1}, {"U": 1, "A": 1}),
    )

    # backdoor adjustment
    # P(Y=1|do(A=1)) = Sum_{u=0,1} P(Y=1|A=1, U=u)P(U=u)
    # P(Y=1|do(A=1)) = P(Y=1|A=1, U=0)P(U=0) + P(Y=1|A=1, U=1)P(U=1)

    print(
        "P(Y=1|do(A=1)) =",
        conditional_prob(joint_prob, {"Y": 1}, {"U": 0, "A": 1}) * bernoulli(0)
        + conditional_prob(joint_prob, {"Y": 1}, {"U": 1, "A": 1})
        * bernoulli(1),
    )

    # P(Y=1|do(A=0)) = Sum_{u=0,1} P(Y=1|A=0, U=u)P(U=u)
    # P(Y=1|do(A=0)) = P(Y=1|A=0, U=0)P(U=0) + P(Y=1|A=0, U=1)P(U=1)
    print(
        "P(Y=1|do(A=0)) =",
        conditional_prob(joint_prob, {"Y": 1}, {"U": 0, "A": 0}) * bernoulli(0)
        + conditional_prob(joint_prob, {"Y": 1}, {"U": 1, "A": 0})
        * bernoulli(1),
    )
