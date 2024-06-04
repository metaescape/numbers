from integer import Integer
from natural import NaturalNumber


class Rational:
    zero = Integer(NaturalNumber())
    one = Integer(NaturalNumber().successor())

    def __init__(self, a, b=1):
        if isinstance(b, int):
            assert b != 0
        else:
            assert b != Rational.zero
        self.a = a
        self.b = b

    def __eq__(self, other):
        return self.a * other.b == self.b * other.a

    def __repr__(self) -> str:
        return f"{self.a} // {self.b}"

    def __neg__(self):
        return Rational(-self.a, self.b)

    def __add__(self, other):
        return Rational(self.a * other.b + self.b * other.a, self.b * other.b)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        return Rational(self.a * other.a, self.b * other.b)

    def __reverse__(self):
        assert self.a != 0
        return Rational(self.b, self.a)

    def __abs__(self):
        return Rational2(abs(self.a), abs(self.b))

    def __truediv__(self, other):
        return self * other.__reverse__()

    def __le__(self, other):
        return lesseq0(self + (-other))

    def __lt__(self, other):
        return self <= other and not self == other

    def __pow__(self, n: int):
        if n < 0:
            return (self ** (-n)).__reverse__()

        if n == 0:
            return Rational(1)

        if n % 2 == 0:
            return (self * self) ** (n // 2)
        return self * (self ** (n - 1))


def lesseq0(self):
    return (self.a >= 0 and self.b <= 0) or (self.a <= 0 and self.b >= 0)


def absolute(self):
    return Rational(abs(self.a), abs(self.b))


def distance(x, y):
    return absolute(x - y)


def epsilon_close(x, y, epsilon=Rational(1, 1000)):
    return distance(x, y) <= epsilon


from math import gcd


class Rational2:
    def __new__(cls, a, b=1, *, force_int=False):
        assert b != 0, "Denominator cannot be zero"

        # 化简 a 和 b
        g = gcd(a, b)
        a //= g
        b //= g

        if b == 1 and force_int:
            return int(a)
        else:
            instance = super().__new__(cls)
            instance.a = a
            instance.b = b
            instance.force_int = force_int
            return instance

    def __init__(self, a, b=1, *, force_int=False):
        # 在 __new__ 方法中已经完成属性初始化，无需重复初始化
        pass

    def __repr__(self):
        if self.b == 1:
            return str(self.a)
        else:
            return f"{self.a}/{self.b}"

    def _check_int_and_convert(self, other):
        if isinstance(other, int):
            return Rational2(other, 1)
        return other

    def __eq__(self, other):
        # only consider int and Rational2 type
        other = self._check_int_and_convert(other)
        return self.a * other.b == self.b * other.a

    def __add__(self, other):
        other = self._check_int_and_convert(other)
        return Rational2(self.a * other.b + self.b * other.a, self.b * other.b)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return -(self - other)

    def __mul__(self, other):
        other = self._check_int_and_convert(other)
        return Rational2(self.a * other.a, self.b * other.b)

    def __rmul__(self, other):
        return self * other

    def __reverse__(self):
        assert self.a != 0, "cannot reverse 0"
        return Rational2(self.b, self.a)

    def __truediv__(self, other):
        other = self._check_int_and_convert(other)
        return self * other.__reverse__()

    def __rtruediv__(self, other):
        other = self._check_int_and_convert(other)
        return other / self

    def __neg__(self):
        return Rational2(-self.a, self.b)

    def __abs__(self):
        return Rational2(abs(self.a), abs(self.b))

    def __le__(self, other):
        other = self._check_int_and_convert(other)
        return lesseq0(self + (-other))

    def __lt__(self, other):
        return self <= other and not self == other

    def __ge__(self, other):
        other = self._check_int_and_convert(other)
        return other <= self

    def __gt__(self, other):
        other = self._check_int_and_convert(other)
        return other < self

    def __pow__(self, n: int):
        if n < 0:
            return (self ** (-n)).__reverse__()

        if n == 0:
            return Rational2(1)

        if n % 2 == 0:
            return (self * self) ** (n // 2)
        return self * (self ** (n - 1))


if __name__ == "__main__":

    # 测试代码
    r1 = Rational2(1, force_int=True)  # 1
    r2 = Rational2(3, 4)
    r3 = 2

    assert type(r1) == int
    assert type(r2) == Rational2
    assert type(r3) == int
    assert r2 + r1 == Rational(7, 4)  # Rational2 + int supported by __add__
    assert r1 + r2 == Rational(7, 4)  # int + Rational2  supported by __radd__
    assert r2 - r1 == -Rational(1, 4)  # Rational2 - int supported by __sub__
    assert r1 - r2 == Rational(1, 4)  # int - Rational2  supported by __rsub__
    assert r3 * r2 == Rational(3, 2)  # Rational2 * int supported by __mul__
    assert r2 * r3 == Rational(3, 2)  # int * Rational2  supported by __rmul__
    assert r2 / r3 == Rational(
        3, 8
    )  # Rational2 /  int supported by __truediv__
    assert r3 / r2 == Rational(
        8, 3
    )  # Rational2 / int supported by __truediv__
    assert r2**r3 == Rational(9, 16)  # Rational2 ** int supported by __pow__
