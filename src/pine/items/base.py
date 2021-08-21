# Standard Library
import abc
import html
from pathlib import Path

# Third-Party
import pyduktape
from cstream import stdwar
from ..pinelib import Stack, Source

class mdType(object, metaclass=abc.ABCMeta):
    """"""

    TAB = "\t"

    __lang__ = None
    lang_set = set()

    path_stack = Stack()

    __indent__ = 0
    __inline__ = False
    
    # -*- Basic Interface -*-
    def __init__(self, *child: tuple, path: str = None):
        self._keys = {}
        self.child = [c for c in child if c]

        self.lexinfo = {
            'lexpos': 0,
            'chrpos': 0,
            'lineno': 0,
            'source': None
        }

        self.__path__ = Path(path).resolve(strict=True) if path is not None else None

    @property
    def lineno(self) -> int:
        return self.lexinfo['lineno']

    @property
    def lexpos(self) -> int:
        return self.lexinfo['lexpos']

    @property
    def chrpos(self) -> int:
        return self.lexinfo['chrpos']

    @property
    def source(self) -> Source:
        return self.lexinfo['source']

    @property
    def keys(self) -> dict:
        return self._keys

    def __iter__(self):
        return iter(c for c in self.child if c)

    def __getitem__(self, key: str):
        return self.keys[key]

    def __setitem__(self, key: str, value: object):
        self.keys[key] = value

    def append(self, c: object):
        self.child.append(c)

    def update(self, d: dict):
        for key, value in d.items():
            self.keys[key] = value

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.child)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(repr, self.child))})"

    # -*- Language -*-
    @classmethod
    def add_lang(cls, lang: str) -> str:
        if lang is not None:
            cls.lang_set.add(lang)
        return lang

    @classmethod
    def set_lang(cls, lang: str) -> str:
        cls.__lang__ = lang

    @classmethod
    def get_lang(cls) -> str:
        return cls.__lang__

    # -*- Indent -*-
    @property
    def pad(self):
        return self.TAB * self.__indent__

    @classmethod
    def _reset(self) -> str:
        self.__indent__ += 1

    @classmethod
    def _push(self) -> str:
        self.__indent__ += 1

    @classmethod
    def _pop(self) -> str:
        self.__indent__ -= 1

    @property
    def reset(self):
        self._reset()
        return str()

    @property
    def push(self) -> str:
        self._push()
        return str()

    @property
    def pop(self) -> str:
        self._pop()
        return str()

    @classmethod
    def _inline(cls) -> bool:
        return bool(cls.__inline__)

    @property
    def inline(self) -> bool:
        return self._inline()

    # -*- Tag options -*-
    def get_option(self, key: str) -> str:
        return f' {key}="{self[key]}"' if bool(self[key]) else str()


    @property
    def options(self) -> str:
        return "".join(self.get_option(key) for key in self.keys)

    # -*- Path Properties -*-
    @property
    def path(self) -> Path:
        return self.path_stack.top

    # -*- Render -*-
    @abc.abstractproperty
    def html(self) -> str:
        pass

    @classmethod
    def html_format(cls, x: object):
        if isinstance(x, mdType):
            return x.html
        elif x:
            return str(x)
        else:
            return str()

    @abc.abstractproperty
    def tex(self) -> str:
        pass

    @classmethod
    def tex_format(cls, x: object):
        if isinstance(x, mdType):
            return x.tex
        elif x:
            return str(x)
        else:
            return str()

    def tex_usepackage(self, package: str):
        raise NotImplementedError

    @classmethod
    def html_escape(cls, text: str, quote: bool = False):
        return html.escape(text, quote=quote)

    @classmethod
    def tex_escape(cls, text: str, quote: bool = False):
        raise NotImplementedError

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

    def __init__(self, *child: tuple, path: str = None):
        mdType.__init__(self, *child)

        if path is None:
            self.file_path = None
        else:
            self.file_path = Path(str(path)).resolve(strict=True)

    @property
    def html(self):
        self.path_stack.push(self.file_path)
        html = f"\n{self.pad}".join(self.html_format(c) for c in self)
        self.path_stack.pop()
        return html

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
        return "\n".join(map(str, self.child))

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