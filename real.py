import random
from itertools import islice
from itertools import count
from rational import Rational2


def final_e_stable(gen_func, n=20, e=Rational2(1, 200)):
    gen = gen_func()
    elements = list(islice(gen, n, n + 5))
    for _ in range(5):
        ele1, ele2 = random.sample(elements, 2)
        if abs(ele1 - ele2) > e:
            return False
    return True


def seq_equal(gen_func1, gen_func2, n=20, e=Rational2(1, 20)):
    gen1 = gen_func1()
    gen2 = gen_func2()
    elements1 = list(islice(gen1, n, n + 5))
    elements2 = list(islice(gen2, n, n + 5))
    for ele1, ele2 in zip(elements1, elements2):
        if abs(ele1 - ele2) > e:
            return False
    return True


def gen_1_n():
    for n in count(start=1):
        yield Rational2(1, n)


def gen_2_n():
    for n in count(start=1):
        yield Rational2(2, n)


def gen_1_0000():
    for n in count(start=1):
        yield 1 + 1 / Rational2(10) ** n


def gen_0_9999():
    for n in count(start=1):
        yield 1 - 1 / Rational2(10) ** n


def sup(is_upper_bound, low=0, high=100):
    for n in count(start=2):
        m_n = find_M(is_upper_bound, low, high, n)
        yield m_n


def find_M(is_upper_bound, low, high, n):
    assert not is_upper_bound(low)
    assert is_upper_bound(high)
    low, high = low * n, high * n
    while 1:
        mid = (low + high) // 2
        left = not is_upper_bound(Rational2(mid - 1, n))
        right = is_upper_bound(Rational2(mid, n))
        if not left:
            high = mid
        elif not right:
            low = mid
        else:
            return Rational2(mid, n)


def n_sqrt_root(x, n, y):
    return y**n > x


if __name__ == "__main__":

    from functools import partial

    sqrt_root_2 = sup(partial(n_sqrt_root, 2, 2))
    for i in range(1, 100):
        print(next(sqrt_root_2))
