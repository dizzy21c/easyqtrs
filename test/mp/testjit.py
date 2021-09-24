import numba as nb
import numpy as np
import timeit

# 普通的 for
def add1(x, c):
    rs = [0.] * len(x)
    for i, xx in enumerate(x):
        rs[i] = xx + c
    return rs

# list comprehension
def add2(x, c):
    return [xx + c for xx in x]

# 使用 jit 加速后的 for
@nb.jit(nopython=True)
# @nb.jit
def add_with_jit(x, c):
    rs = [0.] * len(x)
    for i, xx in enumerate(x):
        rs[i] = xx + c
    return rs

y = np.random.random(10**5).astype(np.float32)
x = y.tolist()

assert np.allclose(add1(x, 1), add2(x, 1), add_with_jit(x, 1))
print(timeit.timeit('add1(x, 1)', globals=globals(), number=10))
print(timeit.timeit('add2(x, 1)', globals=globals(), number=10))
print(timeit.timeit('add_with_jit(x, 1)', globals=globals(), number=10))
# timeit add2(x, 1)
# timeit add_with_jit(x, 1)
# print(np.allclose(wrong_add(x, 1), 1))
