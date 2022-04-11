from tqdm import tqdm
from enum import Enum


class BarFormat(Enum):
    DEFAULT = "{desc:20.20s}: {percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt} [{elapsed}<{remaining},{rate_fmt}{postfix}]"
    SLEEPER = "{desc:20.20s}: {percentage:3.0f}%|{bar}| {n:.0f}/{total_fmt} [{elapsed}<{remaining}"


class Progress:

    __progress = None
    __errors = 0
    __value = 0

    def __init__(self, total, desc, unit="photos", color="green", bar_format=None):
        if not bar_format:
            bar_format = BarFormat.DEFAULT.value
        self.__progress = tqdm(
            total=total, desc=desc, unit=unit, colour=color, bar_format=bar_format
        )
        self.__progress.set_postfix(errors=self.__errors)

    @property
    def value(self) -> int:
        return self.__value

    @property
    def desc(self) -> str:
        return self.__progress.desc

    @desc.setter
    def desc(self, value):
        self.__progress.desc = f"{value}"

    @property
    def total(self) -> int:
        return self.__progress.total

    @total.setter
    def total(self, value):
        self.__progress.total = value

    def write(self, text):
        self.__progress.write(str(text))

    def update(self, inc=1):
        self.__progress.update(inc)
        self.__value += inc

    def error(self, inc=1, *args, **kwargs):
        self.__errors += inc
        self.__progress.set_postfix(errors=self.__errors)
        self.update(inc)

    def close(self):
        self.__progress.close()

    def reset(self):
        self.__progress.reset()
