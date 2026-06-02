import time
from contextlib import contextmanager


@contextmanager
def timer(name: str):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"{name}耗时: {end - start:.2f} 秒")
