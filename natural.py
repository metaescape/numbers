class NaturalNumber:
    def __init__(self, predecessor=None):
        self.is_zero = True if not predecessor else False
        self.predecessor = predecessor

    def successor(self):
        return NaturalNumber(self)

    def __eq__(self, other):
        return eq(self, other)

    def __add__(self, other):
        if self.is_zero:
            return other
        return (self.predecessor + other).successor()

    def __le__(self, other):
        if self == other:
            return True
        elif self.is_zero:
            return True  # 任何数都大于或等于零
        elif other.is_zero:
            return False  # 非零数不可能小于零
        else:
            return self.predecessor.__le__(other.predecessor)

    def __lt__(self, other):
        return self <= other and not self == other

    def __mul__(self, other):
        if self.is_zero:
            return self
        return (self.predecessor * other) + other

    def __pow__(self, other):
        if other.is_zero:
            return NaturalNumber(NaturalNumber())
        return self * other.predecessor * self

    def __repr__(self):
        return lambda self: notation(self, 10)


def eq(x, y):
    if x is None or y is None:
        return x is y
    return eq(x.predecessor, y.predecessor)


digits = [
    "0️⃣",
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
]


def notation(self, n):
    assert 2 <= n <= 16
    cnt = 0
    p = self.predecessor
    while p:
        cnt += 1
        p = p.predecessor

    result = []
    while cnt:
        result.append(digits[cnt % n])
        cnt //= n

    return "".join(result[::-1])


def generate_nats(n=30):
    nat = [NaturalNumber()]
    for i in range(n):
        nat.append(nat[-1].successor())
    return nat


nat = generate_nats()
