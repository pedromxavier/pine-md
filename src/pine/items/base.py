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

    def __init__(self, *child: tuple):
        self._data = {"id": "", "class": ""}
        self.child = list(child)

    def __iter__(self):
        return iter(c for c in self.child if c)

    def __getitem__(self, key: str):
        return self._data[key]

    def __setitem__(self, key: str, value: object):
        self._data[key] = value

    def append(self, c: object):
        self.child.append(c)

    def update(self, d: dict):
        for key, value in d.items():
            self._data[key] = value

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.child)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

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

    @classmethod
    def escape(cls, text: str, quote: bool = False):
        return html.escape(text, quote=quote)

    @property
    def tree(self) -> list:
        if not self.child:
            return (self, None)
        else:
            return (self, [c.tree for c in self.child if isinstance(c, mdType)])


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

class mdContents(mdType):
    """"""

    @property
    def html(self):
        return f"\n{self.pad}".join(f"{c.html}" for c in self)