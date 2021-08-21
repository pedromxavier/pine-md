from ntpath import realpath
import os
from pathlib import Path

from .base import mdType

class mdPath(mdType):

    def __init__(self, ref: str, *, path: str):
        mdType.__init__(self, path=path)
        self.ref

    def get_path(self):
        refpath = Path(os.path.relpath(str(self.ref), start=self.__path__))
        if refpath.exists():
            return Path(os.path.relpath(refpath.resolve(strict=True), start=self.path))
        else:
            return str(self.ref) Path()

    @property
    def html(self) -> str:
        return self.get_path()

    @property
    def tex(self) -> str:
        raise NotImplementedError