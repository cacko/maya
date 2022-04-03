from pathlib import Path
from os import walk
from functools import reduce
from glob import glob
from typing import Generator


class Local:
    __root: Path = None
    EXTENSIONS = ["jpg", "JPG", "png"]

    def __init__(self, path: Path) -> None:
        self.__root = path

    def __iter__(self) -> Generator[Path, None, None]:
        for f in self.__walk(self.__root):
            if f.suffix.lstrip(".") in self.EXTENSIONS:
                yield f

    def __len__(self):
        root = self.__root.as_posix()
        return reduce(lambda r, x: r + len(glob(f"{root}/**/*.{x}", recursive=True)), self.EXTENSIONS, 0)

    def __walk(self, root: Path) -> Generator[Path, None, None]:
        for parent, dirs, files in walk(root.resolve()):
            for f in files:
                yield Path(parent) / f
            for d in dirs:
                yield from self.__walk(Path(parent) / d)
