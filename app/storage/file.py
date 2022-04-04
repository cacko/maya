from io import FileIO
import gzip
from pathlib import Path


class StorageFile(object):
    __writer: FileIO = None
    __lines_count: int = 0

    def __init__(self, output_path: Path):
        if output_path.as_posix().endswith(".gz"):
            self.__writer = gzip.open(output_path.as_posix(), "wb")
        else:
            self.__writer = output_path.open("wb")
        self.__writer.write(b"[")

    def write(self, value: str):
        if self.__lines_count:
            self.__writer.write(b",")
        self.__writer.write(value.encode())
        self.__lines_count += 1
        self.__writer.write(b"\n")
        if self.__lines_count % 100 == 0:
            self.__writer.flush()

    def __del__(self):
        self.__writer.write(b"]")
        self.__writer.close()
