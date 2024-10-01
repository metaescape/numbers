# P(S = L) = 0.49
# P(A = N | S = L) = 0.77
# P(A = N | S = R) = 0.24
# P(Y = 1 | S = L, A = N) = 0.73
# P(Y = 1 | S = L, A = O) = 0.69
# P(Y = 1 | S = R, A = N) = 0.93
# P(Y = 1 | S = R, A = O) = 0.87
"""
A --> Y
^     ^
 \   /
   S
"""


def prob_s(s):
    if s == "L":
        return 0.49
    else:
        return 1 - 0.49


def conditional_a_s(a, s):
    if a == "N":
        if s == "L":
            return 0.77
        else:
            return 0.24
    else:
        return 1 - conditional_a_s("N", s)


def conditional_y_as(y, a, s):
    if y == 1:
        if s == "L":
            if a == "N":
                return 0.73
            else:
                return 0.69
        else:
            if a == "N":
                return 0.93
            else:
                return 0.87
    else:
        return 1 - conditional_y_as(1, a, s)


def joint_prob(assignments):
    return (
        prob_s(assignments["S"])
        * conditional_a_s(assignments["A"], assignments["S"])
        * conditional_y_as(
            assignments["Y"], assignments["A"], assignments["S"]
        )
    )


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


def assign_remap(assignments):
    for key in list(assignments.keys()):
        if key == "S":
            if assignments[key] == 0:
                assignments[key] = "L"
            else:
                assignments[key] = "R"
        if key == "A":
            if assignments[key] == 0:
                assignments[key] = "N"
            else:
                assignments[key] = "O"


def conditional_prob(joint_prob, targets: dict, conditions: dict = {}):

    queries = {**targets, **conditions}

    remains1 = list(set(["Y", "A", "S"]) - set(queries.keys()))

    numerator = 0
    for assignment in generate_all_assignments(remains1):
        assign_remap(assignment)
        numerator += joint_prob({**assignment, **queries})

    if len(conditions) == 0:
        return numerator

    remains2 = list(set(["A", "S", "Y"]) - set(conditions.keys()))
    denominator = 0
    for assignment in generate_all_assignments(remains2):
        assign_remap(assignment)
        denominator += joint_prob({**assignment, **conditions})
    return numerator / denominator


if __name__ == "__main__":
    print("P(S = L) =", prob_s("L"))
    print("P(A = N | S = L) =", conditional_a_s("N", "L"))
    print("P(A = N | S = R) =", conditional_a_s("N", "R"))
    print("P(Y = 1 | S = L, A = N) =", conditional_y_as(1, "N", "L"))
    print("P(Y = 1 | S = L, A = O) =", conditional_y_as(1, "O", "L"))
    print("P(Y = 1 | S = R, A = N) =", conditional_y_as(1, "N", "R"))
    print("P(Y = 1 | S = R, A = O) =", conditional_y_as(1, "O", "R"))
    print(
        "P(Y=1 |A = N) =", conditional_prob(joint_prob, {"Y": 1}, {"A": "N"})
    )
    print(
        "P(Y=1 |A = O) =", conditional_prob(joint_prob, {"Y": 1}, {"A": "O"})
    )
