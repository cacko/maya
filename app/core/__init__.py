import time
from contextlib import contextmanager


@contextmanager
def perf_time(name):
    st = time.perf_counter()
    try:
        yield
    finally:
        total = time.perf_counter() - st
        print(f"{name} -> {total}s")