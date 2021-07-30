# Standard Library
import abc
import html
from pathlib import Path

# Third-Party
import pyduktape
from cstream import stdwar

from ..pinelib import trackable


@trackable
class mdType(object, metaclass=abc.ABCMeta):
    """"""

    TAB = "\t"

    __inline__ = False

    __data__ = {"stack": 0}

    __pine__ = None

    @classmethod
    def _add_pine(cls, pine: type):
        cls.__pine__ = pine

    @property
    def pine(self) -> type:
        if self.__pine__ is None:
            raise UnboundLocalError("Call to 'mdType._add_pine' is missing.")
        else:
            return self.__pine__

    def __init__(self, *child: tuple):
        self._data = {"id": "", "class": ""}
        self.child = [c for c in child if c]

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
        return f"{self.__class__.__name__}({', '.join(map(repr, self.child))})"

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

    @abc.abstractproperty
    def tex(self) -> str:
        pass

    def tex_usepackage(self, package: str):
        raise NotImplementedError

    @classmethod
    def html_escape(cls, text: str, quote: bool = False):
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

    @property
    def tex(self) -> str:
        return str()

class mdDocument(mdType):

    @property
    def html(self):
        return f"\n{self.pad}".join(e for e in (c.html if isinstance(c, mdType) else str(c) for c in self) if e)

    @property
    def tex(self):
        return f"{self.tex_preamble}{self.tex_document}"

    @property
    def tex_preamble(self):
        raise NotImplementedError

    @property
    def tex_document(self):
        raise NotImplementedError

class mdJavascript(mdType):

    __js__ = None

    @classmethod
    def _js_context(cls):
        if cls.__js__ is None:
            cls.__js__ = pyduktape.DuktapeContext()
        return cls.__js__

    @property
    def js_context(self):
        return self._js_context()

    @property
    def code(self) -> str:
        return '\n'.join(map(str, self.child))

    @property
    def javascript(self) -> str:
        try:
            answer = self.js_context.eval_js(self.code)
            if answer is None:
                return str()
            else:
                return str(answer)
        except pyduktape.JSError as error:
            stdwar[1] << self.code
            stdwar[1] << error
            return str()

    @property
    def html(self) -> str:
        return self.javascript

    @property
    def tex(self) -> str:
        return self.javascript

class mdPath(mdType):

    def __init__(self, path: str, root: str):
        self.path = Path(path).relative_to(Path(root))

    @property
    def html(self) -> str:
        return str(self.path)

    @property
    def tex(self) -> str:
        return str(self.path)