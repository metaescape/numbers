def f():
    num = 123

    def decode(num):
        res = ""
        while num:
            res = res + chr(num % 256)
            num //= 256
        return res

    print(decode(num))


def replace_num(code, num):
    code_lines = code.strip().split("\n")
    num_str = []
    while num:
        num_str.append(str(num % 10))
        num //= 10
    num_str = "".join(num_str[::-1])
    code_lines[1] = "    num = " + num_str
    return "\n".join(code_lines)


base = """
def f():
    num = 0

    def decode(num):
        res = ""
        while num:
            res = chr(num % 256) + res
            num //= 256
        return res

    print(decode(num))
"""


def search_self():

    high = encode(replace_num(base, encode(base)))
    for i in range(3):
        high = encode(replace_num(base, high))
    low = encode(base)
    while low < high:
        mid = (high + low) // 2
        program_num = encode(replace_num(base, mid))
        if mid == program_num:
            print("find fix point")
            return decode(mid)
        elif mid < program_num:
            high = mid - 1
        else:
            low = mid + 1

    return None


def decode(num):
    res = ""
    while num:
        res = res + chr(num % 256)
        num //= 256
    return res


def encode(program):
    res = 0
    for ch in program[::-1]:
        res = res * 256 + ord(ch)
    return res


if __name__ == "__main__":
    program = """
    def encode(program):
        res = 0
        for ch in program:
            res = res * 2 + ord(ch)
        return res
    """
    # print(encode(program))

    # print(search_self())

    print(decode(encode(program)))
    # print(search_self())
    # print(replace_num(base, 1000))
    print(encode("12234234234"))
