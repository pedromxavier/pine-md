import itertools as it
from dataclasses import dataclass

from cstream import stdwar

from ..items import mdText, mdHeader
from ..items import mdItalic, mdBold, mdCode, mdStrike

@dataclass
class Flags(object):
    i: int = 0
    b: int = 0
    s: int = 0
    c: int = 0
    html: int = 0
    head: int = 0
    body: int = 0
    text: int = 0
    ulist: int = 0
    olist: int = 0
    indent: int = 0
    header: int = 0
    last_indent: int = 0
    
class CodeGenerator:
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

state = CodeGenerator(0)

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
### ------------------------

## TRANSITIONS
transition = CodeGenerator(0)

## BASIC TRANSITIONS
T_ENDL = transition("T_ENDL")
T_SKIP = transition("T_SKIP")
T_INDENT = transition("T_INDENT")

## Characters
T_PUSH_CHAR = transition("T_PUSH_CHAR")
T_FLUSH_CHAR = transition("T_FLUSH_CHAR")
T_PUSH_FLUSH_CHAR = transition("T_PUSH_FLUSH_CHAR")
T_FLUSH_PUSH_CHAR = transition("T_FLUSH_PUSH_CHAR")

## HTML STUFF
T_PUSH_HTML = transition("T_PUSH_HTML")
T_PUSH_HEAD = transition("T_PUSH_HEAD")
T_PUSH_BODY = transition("T_PUSH_BODY")
T_INIT_TEXT = transition("T_INIT_TEXT")
T_PUSH_TEXT = transition("T_PUSH_TEXT")
T_PUSH_SPACE = transition("T_PUSH_SPACE")
T_INIT_HEADER = transition("T_INIT_HEADER")
T_PUSH_HEADER = transition("T_PUSH_HEADER")

## PINE COMMANDS
T_INC_GET = transition("T_INC_GET")
T_VAR_SET = transition("T_VAR_SET")
T_VAR_GET = transition("T_VAR_GET")

## MARKDOWN STUFF
## TEXT EFFECTS
T_TEXT_I = transition("T_TEXT_I")
T_TEXT_B = transition("T_TEXT_B")
T_TEXT_S = transition("T_TEXT_S")
T_TEXT_C = transition("T_TEXT_C")

T_LOAD_TRIGGER = transition("T_LOAD_TRIGGER")
T_LINK_STAR_TRIGGER = transition("T_LINK_STAR_TRIGGER")
T_LINK_PUSH = transition("T_LINK_PUSH")
T_LINK_LOAD_PUSH = transition("T_LINK_LOAD_PUSH")
T_LINK_LOAD_POP = transition("T_LINK_LOAD_POP")
T_LINK_POP = transition("T_LINK_POP")
T_TEXT_VAR = transition("T_TEXT_VAR")

T_DIV_START = transition("T_DIV_START")
T_DIV_INIT = transition("T_DIV_INIT")
T_DIV_PUSH = transition("T_DIV_PUSH")
T_DIV_POP = transition("T_DIV_POP")
T_DIV_TAG_PUSH = transition("T_DIV_TAG_PUSH")
T_DIV_TAG_POP = transition("T_DIV_TAG_POP")
T_DIV_CLASS_PUSH = transition("T_DIV_CLASS_PUSH")
T_DIV_CLASS_POP = transition("T_DIV_CLASS_POP")
T_DIV_ID_PUSH = transition("T_DIV_ID_PUSH")
T_DIV_ID_POP = transition("T_DIV_ID_POP")

T_ULIST_ITEM = transition("T_ULIST_ITEM")
T_OLIST_ITEM = transition("T_OLIST_ITEM")



states = {
    SKIP: {
        r"[^\S\r\n]": (SKIP, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    COMMENT: {
        r"[^\r\n]": (COMMENT, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    NEW_LINE: {  # START
        r"h": (HTML_0, [T_SKIP]),
        r"b": (BODY_0, [T_SKIP]),
        r"\t": (INDENT, [T_INDENT]),
        r"\/": (PINE_INC, [T_SKIP]),
        r"\$": (PINE_VAR, [T_SKIP]),
        r"\ ": (INDENT_0, [T_SKIP]),
        r"\#": (COMMENT, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    MARKDOWN: {
        r"\_": (MARKDOWN, [T_TEXT_I]),
        r"\*": (MARKDOWN, [T_TEXT_B]),
        r"\~": (MARKDOWN, [T_TEXT_S]),
        r"\`": (MARKDOWN, [T_TEXT_C]),
        r"\[": (MD_LINK_LOAD_PUSH, [T_LINK_LOAD_PUSH]),
        r"\]": (MD_LINK_LOAD_POP, [T_LINK_LOAD_POP]),
        r"\)": (MD_LINK_POP, [T_LINK_POP]),
        r"\$": (MD_TEXT_VAR, [T_SKIP]),
        r"\\": (MD_TEXT_ESCAPE, [T_SKIP]),
        r"[^\S\r\n]": (MARKDOWN, [T_PUSH_SPACE]),
        r"[^\r\n]": (MD_TEXT, [T_PUSH_CHAR]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    MD_TEXT: {
        r"[^\S\r\n]": (MD_TEXT, [T_PUSH_SPACE]),
        r"[^\r\n\_\*\~\`\[\]\(\)\$\\]": (MD_TEXT, [T_PUSH_CHAR]),
        None: (MARKDOWN, [T_PUSH_FLUSH_CHAR, T_INIT_TEXT,  None]),
    },
    MD_TEXT_ESCAPE: {
        r"[^\r\n]": (MARKDOWN, [T_PUSH_CHAR]),
    },
    MD_TEXT_VAR: {
        r"[a-zA-Z\_]": (MD_TEXT_VARNAME, [T_PUSH_CHAR]),
    },
    MD_TEXT_VARNAME: {
        r"[a-zA-Z\_]": (MD_TEXT_VARNAME, [T_PUSH_CHAR]),
        None: (MARKDOWN, [T_PUSH_FLUSH_CHAR, T_INIT_TEXT, T_VAR_GET, None]),
    },
    INDENT: {
        r"\{": (MD_DIV_PUSH, [T_DIV_START]),
        r"\}": (MD_DIV_POP, [T_DIV_POP]),
        r"\-": (MD_ULIST, [T_ULIST_ITEM]),
        r"\+": (MD_ULIST, [T_OLIST_ITEM]),
        r"\#": (MD_HEADER, [T_INIT_HEADER]),
        r"[^\s\r\n]": (MARKDOWN, [None]),
        r"[^\S\r\n]": (INDENT, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    INDENT_0: {
        r"\ ": (INDENT_1, [T_SKIP]),
        r"\t": (INDENT, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    INDENT_1: {
        r"\ ": (INDENT_2, [T_SKIP]),
        r"\t": (INDENT, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    INDENT_2: {
        r"\ ": (INDENT, [T_SKIP]),
        r"\t": (INDENT, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    HTML_0: {  # HEAD_0
        r"t": (HTML_1, [T_SKIP]),
        r"e": (HEAD_1, [T_SKIP]),
    },
    HTML_1: {
        r"m": (HTML_2, [T_SKIP]),
    },
    HTML_2: {
        r"l": (HTML, [T_SKIP]),
    },
    HTML: {
        r"[^\S\r\n]": (SKIP, [T_PUSH_HTML]),
        r"[\r\n]": (NEW_LINE, [T_PUSH_HTML]),
    },
    HEAD_1: {
        r"a": (HEAD_2, [T_SKIP]),
    },
    HEAD_2: {
        r"d": (HEAD, [T_SKIP]),
    },
    HEAD: {
        r"[^\S\r\n]": (SKIP, [T_PUSH_HEAD]),
        r"[\r\n]": (NEW_LINE, [T_PUSH_HEAD]),
    },
    BODY_0: {
        r"o": (BODY_1, [T_SKIP]),
    },
    BODY_1: {
        r"d": (BODY_2, [T_SKIP]),
    },
    BODY_2: {
        r"y": (BODY, [T_SKIP]),
    },
    BODY: {
        r"[^\S\r\n]": (SKIP, [T_PUSH_BODY]),
        r"[\r\n]": (NEW_LINE, [T_PUSH_BODY]),
    },
    PINE_INC: {
        r"\t": (PINE_INC_INDENT, [T_SKIP]),
        r"\ ": (PINE_INC_INDENT_0, [T_SKIP]),
    },
    PINE_INC_INDENT: {
        r"[^\S\r\n]": (PINE_INC_SKIP, [T_SKIP]),
        r"\'": (PINE_INC_QUOTE_0, [T_SKIP]),
        r"\"": (PINE_INC_DOUBLEQUOTE_0, [T_SKIP]),
    },
    PINE_INC_INDENT_0: {
        r"\ ": (PINE_INC_INDENT_1, [T_SKIP]),
    },
    PINE_INC_INDENT_1: {
        r"\ ": (PINE_INC_INDENT, [T_SKIP]),
    },
    PINE_INC_SKIP: {
        r"[^\S\r\n]": (PINE_INC_SKIP, [T_SKIP]),
        r"\'": (PINE_INC_QUOTE_0, [T_SKIP]),
        r"\"": (PINE_INC_DOUBLEQUOTE_0, [T_SKIP]),
    },
    PINE_INC_QUOTE_0: {
        r"\'": (PINE_INC_QUOTE_1, [T_PUSH_FLUSH_CHAR, T_INC_GET]),
        r"[^\r\n]": (PINE_INC_QUOTE_TEXT, [None]),
    },
    PINE_INC_QUOTE_TEXT: {
        r"\'": (PINE_INC_QUOTE_1, [T_PUSH_FLUSH_CHAR, T_INC_GET]),
        r"\\": (PINE_INC_QUOTE_TEXT_ESCAPE, [T_SKIP]),
        r"[^\r\n]": (PINE_INC_QUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_INC_QUOTE_TEXT_ESCAPE: {
        r"[^\r\n]": (PINE_INC_QUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_INC_QUOTE_1: {
        r"[^\S\r\n]": (SKIP, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    PINE_INC_DOUBLEQUOTE_0: {
        r"\"": (PINE_INC_DOUBLEQUOTE_1, [T_PUSH_FLUSH_CHAR, T_INC_GET]),
        r"[^\r\n]": (PINE_INC_DOUBLEQUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_INC_DOUBLEQUOTE_TEXT: {
        r"\"": (PINE_INC_DOUBLEQUOTE_1, [T_PUSH_FLUSH_CHAR, T_INC_GET]),
        r"\\": (PINE_INC_DOUBLEQUOTE_TEXT_ESCAPE, [T_SKIP]),
        r"[^\r\n]": (PINE_INC_DOUBLEQUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_INC_DOUBLEQUOTE_TEXT_ESCAPE: {
        r"[^\r\n]": (PINE_INC_DOUBLEQUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_INC_DOUBLEQUOTE_1: {
        r"[^\S\r\n]": (SKIP, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    PINE_VAR: {
        r"\t": (PINE_VAR_INDENT, [T_SKIP]),
        r"\ ": (PINE_VAR_INDENT_0, [T_SKIP]),
    },
    PINE_VAR_INDENT: {
        r"[a-zA-Z\_]": (PINE_VAR_NAME, [T_PUSH_CHAR]),
        r"[^\S\r\n]": (PINE_VAR_SKIP_0, [T_SKIP]),
    },
    PINE_VAR_INDENT_0: {
        r"\ ": (PINE_VAR_INDENT_1, [T_SKIP]),
    },
    PINE_VAR_INDENT_1: {
        r"\ ": (PINE_VAR_INDENT, [T_SKIP]),
    },
    PINE_VAR_SKIP_0: {
        r"[a-zA-Z\_]": (PINE_VAR_NAME, [T_PUSH_CHAR]),
        r"[^\S\r\n]": (PINE_VAR_SKIP_0, [T_PUSH_FLUSH_CHAR]),
    },
    PINE_VAR_NAME: {
        r"[a-zA-Z0-9\_]": (PINE_VAR_NAME, [T_PUSH_CHAR]),
        r"[^\S\r\n]": (PINE_VAR_SKIP_1, [T_PUSH_FLUSH_CHAR]),
    },
    PINE_VAR_SKIP_1: {
        r"[^\S\r\n]": (PINE_VAR_SKIP_1, [T_SKIP]),
        r"\=": (PINE_VAR_EQUAL, [T_SKIP]),
    },
    PINE_VAR_EQUAL: {
        r"[^\S\r\n]": (PINE_VAR_SKIP_2, [T_SKIP]),
    },
    PINE_VAR_SKIP_2: {
        r"[^\S\r\n]": (PINE_VAR_SKIP_2, [T_SKIP]),
        r"\'": (PINE_VAR_QUOTE_0, [T_SKIP]),
        r"\"": (PINE_VAR_DOUBLEQUOTE_0, [T_SKIP]),
    },
    PINE_VAR_QUOTE_0: {
        r"\'": (PINE_VAR_QUOTE_1, [T_PUSH_FLUSH_CHAR, T_VAR_SET]),
        r"[^\r\n]": (PINE_VAR_QUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_VAR_QUOTE_TEXT: {
        r"\'": (PINE_VAR_QUOTE_1, [T_PUSH_FLUSH_CHAR, T_VAR_SET]),
        r"[^\r\n]": (PINE_VAR_QUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_VAR_QUOTE_1: {
        r"[^\S\r\n]": (SKIP, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    PINE_VAR_DOUBLEQUOTE_0: {
        r"\"": (PINE_VAR_DOUBLEQUOTE_1, [T_PUSH_FLUSH_CHAR, T_VAR_SET]),
        r"[^\r\n]": (PINE_VAR_DOUBLEQUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_VAR_DOUBLEQUOTE_TEXT: {
        r"\"": (PINE_VAR_DOUBLEQUOTE_1, [T_PUSH_FLUSH_CHAR, T_VAR_SET]),
        r"[^\r\n]": (PINE_VAR_DOUBLEQUOTE_TEXT, [T_PUSH_CHAR]),
    },
    PINE_VAR_DOUBLEQUOTE_1: {
        r"[^\S\r\n]": (SKIP, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    MD_DIV_PUSH: {
        r"[\r\n]": (NEW_LINE, [T_DIV_INIT]),
        r"[a-zA-Z]": (MD_DIV_HEADER_TAG, [T_PUSH_CHAR]),
        r"[^\S\r\n]": (MD_DIV_HEADER_SKIP_0, [T_SKIP]),
    },
    MD_DIV_HEADER_SKIP_0: {
        r"[\r\n]": (NEW_LINE, [T_DIV_INIT]),
        r"[a-zA-Z]": (MD_DIV_HEADER_TAG, [T_FLUSH_CHAR, T_PUSH_CHAR]),
        r"\#": (MD_DIV_HEADER_ID, [T_DIV_ID_PUSH]),
        r"\.": (MD_DIV_HEADER_CLASS, [T_DIV_CLASS_PUSH]),
        r"[^\S\r\n]": (MD_DIV_HEADER_SKIP_0, [T_SKIP]),
    },
    MD_DIV_HEADER_TAG: {
        r"[a-zA-Z0-9\-]": (MD_DIV_HEADER_TAG, [T_PUSH_CHAR]),
        r"[^\S\r\n]": (MD_DIV_HEADER_SKIP_1, [T_DIV_TAG_POP]),
        r"\#": (MD_DIV_HEADER_ID, [T_DIV_ID_PUSH]),
        r"\.": (MD_DIV_HEADER_CLASS, [T_DIV_CLASS_PUSH]),
        r"[\r\n]": (NEW_LINE, [T_DIV_INIT]),
    },
    MD_DIV_HEADER_SKIP_1: {
        r"\#": (MD_DIV_HEADER_ID, [T_SKIP]),
        r"\.": (MD_DIV_HEADER_CLASS, [T_SKIP]),
        r"[^\S\r\n]": (MD_DIV_HEADER_SKIP_1, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_DIV_INIT]),
    },
    MD_DIV_HEADER_ID: {
        r"[a-zA-Z]": (MD_DIV_HEADER_ID_NAME, [T_PUSH_CHAR]),
    },
    MD_DIV_HEADER_ID_NAME: {
        r"[a-zA-Z0-9\-]": (MD_DIV_HEADER_ID_NAME, [T_PUSH_CHAR]),
        r"[^\S\r\n]": (MD_DIV_HEADER_SKIP_2, [T_PUSH_FLUSH_CHAR]),
        r"\.": (MD_DIV_HEADER_CLASS, [T_PUSH_FLUSH_CHAR]),
        r"[\r\n]": (NEW_LINE, [T_DIV_INIT]),
    },
    MD_DIV_HEADER_SKIP_2: {
        r"\.": (MD_DIV_HEADER_CLASS, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
        r"[^\S\r\n]": (MD_DIV_HEADER_SKIP_2, [T_SKIP]),
    },
    MD_DIV_HEADER_CLASS: {
        r"[a-zA-Z]": (MD_DIV_HEADER_CLASS_NAME, [T_SKIP]),
    },
    MD_DIV_HEADER_CLASS_NAME: {
        r"[a-zA-Z0-9\-]": (MD_DIV_HEADER_CLASS_NAME, [T_SKIP]),
        r"[^\S\r\n]": (MD_DIV_HEADER_SKIP, [T_SKIP]),
        r"\.": (MD_DIV_HEADER_CLASS, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    MD_DIV_HEADER_SKIP: {
        r"\.": (MD_DIV_HEADER_CLASS, [T_SKIP]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
        r"[^\S\r\n]": (MD_DIV_HEADER_SKIP, [T_SKIP]),
    },
    MD_DIV_POP: {
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
        r"[^\S\r\n]": (SKIP, [T_SKIP]),
    },
    MD_ULIST: {
        r"[^\S\r\n]": (MARKDOWN, [T_SKIP]),
    },
    MD_OLIST: {
        r"[^\S\r\n]": (MARKDOWN, [T_SKIP]),
    },
    MD_HEADER: {
        r"[1-6]": (MD_HEADER_NUMBER, [T_PUSH_CHAR, T_PUSH_FLUSH_CHAR]),
    },
    MD_HEADER_NUMBER: {
        r"[^\S\r\n]": (MARKDOWN, [T_SKIP]),
    },
    MD_LINK_LOAD_PUSH: {
        r"\]": (MD_LINK_LOAD_POP, [T_LINK_LOAD_POP]),
        r"[^\S\r\n\[\]]": (MD_LINK_LOAD_HREF, [T_PUSH_CHAR]),
        r"\\": (MD_LINK_LOAD_HREF_ESCAPE, [T_SKIP]),
    },
    MD_LINK_LOAD_HREF: {
        r"\]": (MD_LINK_LOAD_POP, [T_LINK_LOAD_POP]),
        r"[^\S\r\n\[\]]": (MD_LINK_LOAD_HREF, [T_PUSH_CHAR]),
        r"\\": (MD_LINK_LOAD_HREF_ESCAPE, [T_SKIP]),
    },
    MD_LINK_LOAD_HREF_ESCAPE: {
        r"[^\S\r\n]": (MD_LINK_LOAD_HREF, [T_PUSH_CHAR]),
    },
    MD_LINK_LOAD_POP: {
        r"\@": (MD_LOAD, [T_LOAD_TRIGGER]),
        r"\*": (MD_LINK_STAR, [T_LINK_STAR_TRIGGER]),
        r"\(": (MD_LINK_PUSH, [T_LINK_PUSH]),
    },
    MD_LINK_STAR: {
        r"\(": (MD_LINK_PUSH, [T_SKIP]),
    },
    MD_LINK_PUSH: {
        None: (MARKDOWN, [None]),
    },
    MD_LINK_POP: {
        None: (MARKDOWN, [T_LINK_POP]),
    },
    MD_LOAD: {
        None: (MD_LOAD_TYPE, [None]),
    },
    MD_LOAD_TYPE: {
        r"[a-zA-Z]": (MD_LOAD_TYPE, [T_PUSH_CHAR]),
        r"[^\S\r\n]": (MARKDOWN, [None]),
        r"[\r\n]": (NEW_LINE, [T_ENDL]),
    },
    
}


def t_skip(self, char: str):
    """Skip char"""

def t_endl(self, char: str):
    """End line"""
    if self.char_buffer:
        t_push_flush_char(self, char)
    if self.flags.text:
        t_push_text(self, char)
    if self.flags.header:
        t_push_header(self, char)

def t_push_char(self, char: str):
    """Push text char into char buffer
    
    Flags
    -----
        space: bool -> False
    """
    self.char_buffer.push(char)
    self.flags.space = False

def t_flush_char(self, char: str):
    """Flush (clear) char buffer"""
    self.char_buffer.flush()

def t_push_flush_char(self, char: str):
    """Push char buffer flush into stack"""
    self.stack.push(self.char_buffer.flush())

def t_push_space(self, char: str):
    """
    Flags
    -----
        space:bool -> True
    """
    if not self.flags.space:
        self.char_buffer.push(char)
        self.flags.space = True
    else:
        pass

def t_var_set(self, char: str):
    """Set variable"""
    value = self.stack.pop()
    name = self.stack.pop()
    self.set_var(name, value)

def t_var_get(self, char: str):
    """Get variable"""
    name = self.stack.pop()
    self.stack.push(self.get_var(name))

def t_inc_get(self, char: str):
    self.include(self.stack.pop())

def t_init_text(self, char: str):
    self.flags.text += 1

def t_push_text(self, char: str):
    """"""
    if self.flags.text:
        self.stack.push(mdText(*reversed([self.stack.pop() for _ in range(self.flags.text)])))
        self.flags.text = 0
    else:
        pass

def t_init_header(self, char: str):
    self.flags.header: int = 1

def t_push_header(self, char: str):
    """Push Header into stack"""
    content = self.stack.pop()
    heading = int(self.stack.pop())
    Header = mdHeader.new(heading)
    self.stack.push(Header(*content))
    self.flags.header = 0

def t_text_i(self, char: str):
    if self.flags.i:
        if self.tag_stack.top != 'i':
            self.syntax_error()
        else:
            self.tag_stack.pop()
        self.stack.push(mdItalic(self.stack.pop()))
        self.flags.i = 0
    else:
        self.tag_stack.push('i')
        self.flags.i = 1

def t_text_b(self, char: str):
    if self.flags.b:
        if self.tag_stack.top != 'b':
            self.syntax_error()
        else:
            self.tag_stack.pop()
        self.stack.push(mdBold(self.stack.pop()))
        self.flags.b = 0
    else:
        self.tag_stack.push('b')
        self.flags.b = 1

def t_text_c(self, char: str):
    if self.flags.c:
        if self.tag_stack.top != 'c':
            self.syntax_error()
        else:
            self.tag_stack.pop()
        self.stack.push(mdCode(self.stack.pop()))
        self.flags.c = 0
    else:
        self.tag_stack.push('c')
        self.flags.c = 1

def t_text_s(self, char: str):
    if self.flags.s:
        if self.tag_stack.top != 's':
            self.syntax_error()
        else:
            self.tag_stack.pop()
        self.stack.push(mdStrike(self.stack.pop()))
        self.flags.s = 0
    else:
        self.tag_stack.push('s')
        self.flags.s = 1

transitions = {
    T_SKIP: t_skip,
    T_ENDL: t_endl,
    ## CHAR
    T_PUSH_CHAR: t_push_char,
    T_FLUSH_CHAR: t_flush_char,
    T_PUSH_FLUSH_CHAR: t_push_flush_char,

    ## TEXT
    T_TEXT_I : t_text_i,
    T_TEXT_B : t_text_b,
    T_TEXT_C : t_text_c,
    T_TEXT_S : t_text_s,

    T_INIT_TEXT: t_init_text,
    T_PUSH_TEXT: t_push_text,
    T_PUSH_SPACE: t_push_space,

    ## VAR & INC, GET & SET
    T_VAR_SET: t_var_set,
    T_VAR_GET: t_var_get,
    T_INC_GET: t_inc_get,
    
    ## HEADER
    T_INIT_HEADER: t_init_header,
    T_PUSH_HEADER: t_push_header,

    
}