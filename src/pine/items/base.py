# Standard Library
import abc
import html

from ..pinelib import trackable


@trackable
class mdType(object, metaclass=abc.ABCMeta):
    """"""

    TAB = "\t"

    __inline__ = False

    __data__ = {"stack": 0}

    def __init__(self):
        self._data = {"id": "", "class": ""}

    def __getitem__(self, key: str):
        return self._data[key]

    def __setitem__(self, key: str, value: object):
        self._data[key] = value

    def update(self, d: dict):
        for key, value in d.items():
            self._data[key] = value

    def __bool__(self) -> bool:
        return True

    @property
    def pad(self):
        return self.TAB * self.__data__["stack"]

    @property
    def reset(self):
        self.__class__.__data__["stack"] = 0
        return str()

    @property
    def push(self) -> str:
        self.__class__.__data__["stack"] += 1
        return str()

    @property
    def pop(self) -> str:
        self.__class__.__data__["stack"] -= 1
        return str()

    def get_key(self, key: str) -> str:
        return f' {key}="{self[key]}"' if bool(self[key]) else str()

    @property
    def keys(self) -> str:
        return "".join(self.get_key(key) for key in self._data)

    @property
    def inline(self):
        return self.__class__.__inline__

    @abc.abstractproperty
    def html(self) -> str:
        pass

    @property
    def child(self) -> list:
        return None

    @classmethod
    def escape(cls, text: str, quote: bool = False):
        return html.escape(text, quote=quote)


class mdNull(mdType):
    __ref__ = None

    __inline__ = False

    def __new__(cls):
        if cls.__ref__ is None:
            cls.__ref__ = super().__new__(cls)
        return cls.__ref__

    def __init__(self):
        mdType.__init__(self)

    def __bool__(self) -> bool:
        return False

    @property
    def html(self) -> str:
        return str()


class mdContents(list, mdType):
    """"""

    def __init__(self, *contents: tuple):
        list.__init__(self, [c for c in contents if c])
        mdType.__init__(self)

    def __bool__(self):
        return bool(len(self) > 0)

    @property
    def html(self):
        return f"\n{self.pad}".join(f"{c.html}" for c in self)

    @property
    def child(self) -> list:
        return list(self)
