import re
import itertools as it
from ..pinelib import Source
from ..items import mdType

from cstream import stdwar, stderr


class StateGenerator:
    def __init__(self, start: int):
        self.counter = it.count(start)
        self.__table = {}
        self.__codes = {}

    def __call__(self, key: str = None, *, code: int = None):
        if code is None:
            code: int = next(self.counter)
        if key is not None:
            self.__table[code] = key
        return code

    def activate(self, code: int):
        self.__codes[code] = True

    def active(self) -> list:
        return [c for c in self.__table if self.is_active(c)]

    def inactive(self) -> list:
        return [c for c in self.__table if not self.is_active(c)]

    def is_active(self, code: int) -> bool:
        try:
            return self.__codes[code]
        except KeyError:
            return False

    def get_state(self, code: int) -> str:
        try:
            return self.__table[code]
        except KeyError:
            return None


class pineLexer:

    RE_FLAGS = re.UNICODE | re.VERBOSE

    state = StateGenerator(0)

    # BASIC ------------
    SKIP = state("SKIP")
    COMMENT = state("COMMENT")
    NEW_LINE = state("NEW_LINE")
    MARKDOWN = state("MARKDOWN")
    INDENT = state("INDENT")
    INDENT_0 = state("INDENT_0")
    INDENT_1 = state("INDENT_1")
    INDENT_2 = state("INDENT_2")
    # ----------------

    # HTML TAGS ----
    HTML_0 = state("HTML_0")
    HTML_1 = state("HTML_1")
    HTML_2 = state("HTML_2")
    HTML = state("HTML")

    HEAD_0 = state("HEAD_0", code=HTML_0)
    HEAD_1 = state("HEAD_1")
    HEAD_2 = state("HEAD_2")
    HEAD = state("HEAD")

    BODY_0 = state("BODY_0")
    BODY_1 = state("BODY_1")
    BODY_2 = state("BODY_2")
    BODY = state("BODY")
    # --------------

    # PINE CODE -----------------------
    ## INCLUDE ------------------------
    PINE_INC = state("PINE_INC")
    PINE_INC_INDENT = state("PINE_INC_INDENT")
    PINE_INC_INDENT_0 = state("PINE_INC_INDENT_0")
    PINE_INC_INDENT_1 = state("PINE_INC_INDENT_1")
    PINE_INC_SKIP = state("PINE_INC_SKIP")
    PINE_INC_QUOTE_0 = state("PINE_INC_QUOTE_0")
    PINE_INC_QUOTE_TEXT = state("PINE_INC_QUOTE_TEXT")
    PINE_INC_QUOTE_TEXT_ESCAPE = state("PINE_INC_QUOTE_TEXT_ESCAPE")
    PINE_INC_QUOTE_1 = state("PINE_INC_QUOTE_1")
    PINE_INC_DOUBLEQUOTE_0 = state("PINE_INC_DOUBLEQUOTE_0")
    PINE_INC_DOUBLEQUOTE_TEXT = state("PINE_INC_DOUBLEQUOTE_TEXT")
    PINE_INC_DOUBLEQUOTE_TEXT_ESCAPE = state("PINE_INC_DOUBLEQUOTE_TEXT_ESCAPE")
    PINE_INC_DOUBLEQUOTE_1 = state("PINE_INC_DOUBLEQUOTE_1")
    # ---------------------------------

    ## VARIABLE -----------------------
    PINE_VAR = state("PINE_VAR")
    PINE_VAR_INDENT = state("PINE_VAR_INDENT")
    PINE_VAR_INDENT_0 = state("PINE_VAR_INDENT_0")
    PINE_VAR_INDENT_1 = state("PINE_VAR_INDENT_1")
    PINE_VAR_SKIP_0 = state("PINE_VAR_SKIP_0")
    PINE_VAR_NAME = state("PINE_VAR_NAME")
    PINE_VAR_SKIP_1 = state("PINE_VAR_SKIP_1")
    PINE_VAR_EQUAL = state("PINE_VAR_EQUAL")
    PINE_VAR_SKIP_2 = state("PINE_VAR_SKIP_2")
    PINE_VAR_QUOTE_0 = state("PINE_VAR_QUOTE_0")
    PINE_VAR_QUOTE_TEXT = state("PINE_VAR_QUOTE_TEXT")
    PINE_VAR_QUOTE_1 = state("PINE_VAR_QUOTE_1")
    PINE_VAR_DOUBLEQUOTE_0 = state("PINE_VAR_DOUBLEQUOTE_0")
    PINE_VAR_DOUBLEQUOTE_TEXT = state("PINE_VAR_DOUBLEQUOTE_TEXT")
    PINE_VAR_DOUBLEQUOTE_1 = state("PINE_VAR_DOUBLEQUOTE_1")
    # ---------------------------------

    # MARKDOWN -------------------
    ## DIV -----------------------
    MD_DIV_PUSH = state("MD_DIV_PUSH")
    MD_DIV_HEADER_SKIP_0 = state("MD_DIV_HEADER_SKIP_0")
    MD_DIV_HEADER_TAG = state("MD_DIV_HEADER_TAG")
    MD_DIV_HEADER_SKIP_1 = state("MD_DIV_HEADER_SKIP_1")
    MD_DIV_HEADER_ID = state("MD_DIV_HEADER_ID")
    MD_DIV_HEADER_ID_NAME = state("MD_DIV_HEADER_ID_NAME")
    MD_DIV_HEADER_SKIP_2 = state("MD_DIV_HEADER_SKIP_2")
    MD_DIV_HEADER_CLASS = state("MD_DIV_HEADER_CLASS")
    MD_DIV_HEADER_CLASS_NAME = state("MD_DIV_HEADER_CLASS_NAME")
    MD_DIV_HEADER_SKIP = state("MD_DIV_HEADER_SKIP")
    # A LOT HAPPENS HERE!
    MD_DIV_POP = state("MD_DIV_POP")
    ## ---------------------------

    ## LIST ----------------------
    MD_ULIST = state("MD_ULIST")
    MD_OLIST = state("MD_OLIST")
    ## ---------------------------

    ## HEADERS ---------------
    MD_HEADER = state("MD_HEADER")
    MD_HEADER_NUMBER = state("MD_HEADER_NUMBER")
    ## -----------------------

    ## TEXT -------------------
    MD_TEXT = state("MD_TEXT")
    MD_TEXT_ESCAPE = state("MD_TEXT_ESCAPE")
    ### LINK & LOAD -----------
    MD_LINK_LOAD_PUSH = state("MD_LINK_LOAD_PUSH")
    MD_LINK_LOAD_HREF = state("MD_LINK_LOAD_HREF")
    MD_LINK_LOAD_HREF_ESCAPE = state("MD_LINK_LOAD_HREF_ESCAPE")
    MD_LINK_LOAD_POP = state("MD_LINK_LOAD_POP")
    ### LINK ------------------
    MD_LINK_STAR = state("MD_LINK_STAR")
    MD_LINK_PUSH = state("MD_LINK_PUSH")
    # A FEW HAPPENS HERE!
    MD_LINK_POP = state("MD_LINK_POP")
    ### LOAD ------------------
    MD_LOAD = state("MD_LOAD")
    MD_LOAD_TYPE = state("MD_LOAD_TYPE")
    ### VARIABLE ---------------
    MD_TEXT_VAR = state("MD_TEXT_VAR")
    MD_TEXT_VARNAME = state("MD_TEXT_VARNAME")
    ### EFFECTS ----------------
    MD_TEXT_I = state("MD_TEXT_I")
    MD_TEXT_B = state("MD_TEXT_B")
    MD_TEXT_C = state("MD_TEXT_C")
    MD_TEXT_S = state("MD_TEXT_S")
    ### ESCAPE
    MD_ESCAPE = state("MD_ESCAPE")
    ### ------------------------

    # MARKDOWN -------------------

    _states = {
        SKIP: {
            r"[^\S\r\n]": SKIP,
            r"[\r\n]": NEW_LINE,
        },
        COMMENT: {
            r"[^\S\r\n]": COMMENT,
            r"[\r\n]": NEW_LINE,
        },
        NEW_LINE: {  # START
            r"h": HTML_0,
            r"b": BODY_0,
            r"\t": INDENT,
            r"\/": PINE_INC,
            r"\$": PINE_VAR,
            r"\ ": INDENT_0,
            r"\#": COMMENT,
            r"[\r\n]": NEW_LINE,
        },
        MARKDOWN: {
            r"\_": MD_TEXT_I,
            r"\*": MD_TEXT_B,
            r"\~": MD_TEXT_S,
            r"\`": MD_TEXT_C,
            r"\[": MD_LINK_LOAD_PUSH,
            r"\]": MD_LINK_LOAD_POP,
            r"\$": MD_TEXT_VAR,
            r"[^\S\r\n]": MARKDOWN,
            r"[^\r\n]": MD_TEXT,
            r"[\r\n]": NEW_LINE,
        },
        INDENT: {
            r"\{": MD_DIV_PUSH,
            r"\}": MD_DIV_POP,
            r"\-": MD_ULIST,
            r"\+": MD_OLIST,
            r"\#": MD_HEADER,
            r"[^\S\r\n]": INDENT,
            r"[^\r\n]": INDENT,
            r"[\r\n]": NEW_LINE,
        },
        INDENT_0: {
            r"\ ": INDENT_1,
            r"\t": INDENT,
            r"[\r\n]": NEW_LINE,
        },
        INDENT_1: {
            r"\ ": INDENT_2,
            r"\t": INDENT,
            r"[\r\n]": NEW_LINE,
        },
        INDENT_2: {
            r"\ ": INDENT,
            r"\t": INDENT,
            r"[\r\n]": NEW_LINE,
        },
        HTML_0: {  # HEAD_0
            r"t": HTML_1,
            r"e": HEAD_1,
        },
        HTML_1: {
            r"m": HTML_2,
        },
        HTML_2: {
            r"l": HTML,
        },
        HTML: {
            r"[^\S\r\n]": SKIP,
            r"[\r\n]": NEW_LINE,
        },
        HEAD_1: {
            r"a": HEAD_2,
        },
        HEAD_2: {
            r"d": HEAD,
        },
        HEAD: {
            r"[^\S\r\n]": SKIP,
            r"[\r\n]": NEW_LINE,
        },
        BODY_0: {
            r"o": BODY_1,
        },
        BODY_1: {
            r"d": BODY_2,
        },
        BODY_2: {
            r"y": BODY,
        },
        BODY: {
            r"[^\S\r\n]": SKIP,
            r"[\r\n]": NEW_LINE,
        },
        PINE_INC: {
            r"\t": PINE_INC_INDENT,
            r"\ ": PINE_INC_INDENT_0,
        },
        PINE_INC_INDENT: {
            r"[^\S\r\n]": PINE_INC_SKIP,
            r"\'": PINE_INC_QUOTE_0,
            r"\"": PINE_INC_DOUBLEQUOTE_0,
        },
        PINE_INC_INDENT_0: {
            r"\ ": PINE_INC_INDENT_1,
        },
        PINE_INC_INDENT_1: {
            r"\ ": PINE_INC_INDENT,
        },
        PINE_INC_SKIP: {
            r"[^\S\r\n]": PINE_INC_SKIP,
            r"\'": PINE_INC_QUOTE_0,
            r"\"": PINE_INC_DOUBLEQUOTE_0,
        },
        PINE_INC_QUOTE_0: {
            r"\'": PINE_INC_QUOTE_1,
            r"[^\r\n]": PINE_INC_QUOTE_TEXT,
        },
        PINE_INC_QUOTE_TEXT: {
            r"\'": PINE_INC_QUOTE_1,
            r"[^\r\n]": PINE_INC_QUOTE_TEXT,
        },
        PINE_INC_QUOTE_1: {
            r"[^\S\r\n]": SKIP,
            r"[\r\n]": NEW_LINE,
        },
        PINE_INC_DOUBLEQUOTE_0: {
            r"\"": PINE_INC_DOUBLEQUOTE_1,
            r"[^\r\n]": PINE_INC_DOUBLEQUOTE_TEXT,
        },
        PINE_INC_DOUBLEQUOTE_TEXT: {
            r"\"": PINE_INC_DOUBLEQUOTE_1,
            r"[^\r\n]": PINE_INC_DOUBLEQUOTE_TEXT,
        },
        PINE_INC_DOUBLEQUOTE_1: {
            r"[^\S\r\n]": SKIP,
            r"[\r\n]": NEW_LINE,
        },
        PINE_VAR: {
            r"\t": PINE_VAR_INDENT,
            r"\ ": PINE_VAR_INDENT_0,
        },
        PINE_VAR_INDENT: {
            r"[a-zA-Z\_]": PINE_VAR_NAME,
            r"[^\S\r\n]": PINE_VAR_SKIP_0,
        },
        PINE_VAR_INDENT_0: {
            r"\ ": PINE_VAR_INDENT_1,
        },
        PINE_VAR_INDENT_1: {
            r"\ ": PINE_VAR_INDENT,
        },
        PINE_VAR_SKIP_0: {
            r"[^\S\r\n]": PINE_VAR_SKIP_0,
        },
        PINE_VAR_NAME: {
            r"[a-zA-Z0-9\_]": PINE_VAR_NAME,
            r"[^\S\r\n]": PINE_VAR_SKIP_1,
        },
        PINE_VAR_SKIP_1: {
            r"[^\S\r\n]": PINE_VAR_SKIP_1,
            r"\=": PINE_VAR_EQUAL,
        },
        PINE_VAR_EQUAL: {
            r"[^\S\r\n]": PINE_VAR_SKIP_2,
        },
        PINE_VAR_SKIP_2: {
            r"[^\S\r\n]": PINE_VAR_SKIP_2,
            r"\'": PINE_VAR_QUOTE_0,
            r"\"": PINE_VAR_DOUBLEQUOTE_0,
        },
        PINE_VAR_QUOTE_0: {
            r"\'": PINE_VAR_QUOTE_1,
            r"[^\r\n]": PINE_VAR_QUOTE_TEXT,
        },
        PINE_VAR_QUOTE_TEXT: {
            r"\'": PINE_VAR_QUOTE_1,
            r"[^\r\n]": PINE_VAR_QUOTE_TEXT,
        },
        PINE_VAR_QUOTE_1: {
            r"[^\S\r\n]": SKIP,
            r"[\r\n]": NEW_LINE,
        },
        PINE_VAR_DOUBLEQUOTE_0: {
            r"\"": PINE_VAR_DOUBLEQUOTE_1,
            r"[^\r\n]": PINE_VAR_DOUBLEQUOTE_TEXT,
        },
        PINE_VAR_DOUBLEQUOTE_TEXT: {
            r"\"": PINE_VAR_DOUBLEQUOTE_1,
            r"[^\r\n]": PINE_VAR_DOUBLEQUOTE_TEXT,
        },
        PINE_VAR_DOUBLEQUOTE_1: {
            r"[^\S\r\n]": SKIP,
            r"[\r\n]": NEW_LINE,
        },
        MD_DIV_PUSH: {
            r"[\r\n]": NEW_LINE,
            r"[a-zA-Z]": MD_DIV_HEADER_TAG,
            r"[^\S\r\n]": MD_DIV_HEADER_SKIP_0,
        },
        MD_DIV_HEADER_SKIP_0: {
            r"[\r\n]": NEW_LINE,
            r"[a-zA-Z]": MD_DIV_HEADER_TAG,
            r"[^\S\r\n]": MD_DIV_HEADER_SKIP_0,
        },
        MD_DIV_HEADER_TAG: {
            r"[a-zA-Z0-9\-]": MD_DIV_HEADER_TAG,
            r"[^\S\r\n]": MD_DIV_HEADER_SKIP_1,
            r"\#": MD_DIV_HEADER_ID,
            r"\.": MD_DIV_HEADER_CLASS,
            r"[\r\n]": NEW_LINE,
        },
        MD_DIV_HEADER_SKIP_1: {
            r"\#": MD_DIV_HEADER_ID,
            r"\.": MD_DIV_HEADER_CLASS,
            r"[^\S\r\n]": MD_DIV_HEADER_SKIP_1,
            r"[\r\n]": NEW_LINE,
        },
        MD_DIV_HEADER_ID: {
            r"[a-zA-Z]": MD_DIV_HEADER_ID_NAME,
        },
        MD_DIV_HEADER_ID_NAME: {
            r"[a-zA-Z0-9\-]": MD_DIV_HEADER_ID_NAME,
            r"[^\S\r\n]": MD_DIV_HEADER_SKIP_2,
            r"\.": MD_DIV_HEADER_CLASS,
            r"[\r\n]": NEW_LINE,
        },
        MD_DIV_HEADER_SKIP_2: {
            r"\.": MD_DIV_HEADER_CLASS,
            r"[\r\n]": NEW_LINE,
            r"[^\S\r\n]": MD_DIV_HEADER_SKIP_2,
        },
        MD_DIV_HEADER_CLASS: {
            r"[a-zA-Z]": MD_DIV_HEADER_CLASS_NAME,
        },
        MD_DIV_HEADER_CLASS_NAME: {
            r"[a-zA-Z0-9\-]": MD_DIV_HEADER_CLASS_NAME,
            r"[^\S\r\n]": MD_DIV_HEADER_SKIP,
            r"\.": MD_DIV_HEADER_CLASS,
            r"[\r\n]": NEW_LINE,
        },
        MD_DIV_HEADER_SKIP: {
            r"\.": MD_DIV_HEADER_CLASS,
            r"[\r\n]": NEW_LINE,
            r"[^\S\r\n]": MD_DIV_HEADER_SKIP,
        },
        MD_DIV_POP: {
            r"[\r\n]": NEW_LINE,
            r"[^\S\r\n]": SKIP,
        },
        MD_ULIST: {
            r"[^\S\r\n]": MARKDOWN,
        },
        MD_OLIST: {
            r"[^\S\r\n]": MARKDOWN,
        },
        MD_HEADER: {
            r"[1-6]": MD_HEADER_NUMBER,
        },
        MD_HEADER_NUMBER: {
            r"[^\S\r\n]": MARKDOWN,
        },
        MD_TEXT: {},
        MD_LINK_LOAD_PUSH: {
            r"\]": MD_LINK_LOAD_POP,
            r"\\": MD_LINK_LOAD_HREF_ESCAPE,
            r"[^\r\n\[\]]": MD_LINK_LOAD_HREF,
        },
        MD_LINK_LOAD_HREF: {},
        MD_LINK_LOAD_POP: {},
        MD_LINK_STAR: {},
        MD_LINK_PUSH: {},
        MD_LINK_POP: {},
        MD_LOAD: {},
        MD_LOAD_TYPE: {},
        MD_TEXT_VAR: {
            r"[a-zA-Z\_]": MD_TEXT_VARNAME,
        },
        MD_TEXT_VARNAME: {
            r"[a-zA-Z\_]": MD_TEXT_VARNAME,
            r"[^\S\r\n]": MARKDOWN,
            r"[\r\n]": NEW_LINE,
        },
        MD_TEXT_I: {
            None: MARKDOWN,
        },
        MD_TEXT_B: {
            None: MARKDOWN,
        },
        MD_TEXT_C: {
            None: MARKDOWN,
        },
        MD_TEXT_S: {
            None: MARKDOWN,
        },
        MD_ESCAPE: {
            r"[\\\_\~\*\`\[\]\(\)]": MARKDOWN,
        },
    }

    def __init__(self, source: Source, *, ensure_html: bool = False):
        self.ensure_html = bool(ensure_html)
        self.source = source
        self.states = self.compile_states()

        self.flags = {}
        self.stack = []

    def test(self, *args, **kwargs):
        ...

    def parse(self, *, ensure_html: bool = False):
        """"""
        self.ensure_html = bool(ensure_html)
        queue = list(reversed(self.source))
        regex: re.Pattern

        c: int = 0
        r: int = self.NEW_LINE
        s: int

        while queue:
            char: str = queue.pop()
            for regex, s in self.states[r].items():
                if regex is None:  # No match, only redirection.
                    self.trans_debug(r, s, char)
                    r = s
                    break
                elif regex.match(char):
                    self.trans_debug(r, s, char)
                    r = s
                    c += 1
                    break
            else:
                raise SyntaxError("")

        else:
            self.eof()

    def eof(self):
        """"""
        stdwar[0] << "EOF KKKK EAE MAN"

    def compile_states(self) -> dict:
        """"""
        states = {}
        trans: dict
        r: int
        s: int
        for r, trans in self._states.items():
            if r not in states:
                states[r] = {}
            if not trans:
                stdwar[0] << (
                    f"Warning: state '{self.state.get_state(r)}' ({r}) is a dead end."
                )
            for pattern, s in trans.items():
                if pattern is None:
                    regex = None
                else:
                    regex = re.compile(pattern, self.RE_FLAGS)
                states[r][regex] = s
                self.state.activate(s)

        for s in self.state.inactive():
            stdwar[0] << (
                f"Warning: state '{self.state.get_state(s)}' ({s}) is unreachable."
            )

        return states

    def trans(self, r: int, s: int):
        """Transition from state r to s.

        Parameters
        ----------
        r : int
            Current state.
        s : int
            Next state.
        """
        self.trans_debug(r, s)

    def trans_debug(self, r: int, s: int, char: str = None):
        """"""
        if char is None:
            print(f"{r} -> {s}")
        else:
            print(f"{char!r} : {r} -> {s}")
        if s == self.NEW_LINE:
            print()
