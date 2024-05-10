from natural import NaturalNumber


class Integer:
    def __init__(self, a: NaturalNumber, b: NaturalNumber = NaturalNumber()):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return self.a + other.b == self.b + other.a

    def __repr__(self) -> str:
        return f"({self.a}--{self.b})"

    def __add__(self, other):
        return Integer(self.a + other.a, self.b + other.b)

    def __mul__(self, other):
        first = self.a * other.a + self.b * other.b
        second = self.a * other.b + self.b * other.a
        return Integer(first, second)

    def __neg__(self):
        return Integer(self.b, self.a)

    def __le__(self, other):
        return self.a + other.b <= self.b + other.a

    def __lt__(self, other):
        return self <= other and not self == other


def generate_ints(n=30):
    import random

    nat = [NaturalNumber()]
    for i in range(n * 3):
        nat.append(nat[-1].successor())

    ints = {}

    for i in range(-n, n + 1):
        a = random.randint(n, 2 * n)
        b = a - i
        ints[i] = Integer(nat[a], nat[b])

    return ints
