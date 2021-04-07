import re
import itertools as it
from ..pinelib import Source
from ..items import mdType

class StateGenerator:
    def __init__(self, start: int):
        self.counter = it.count(start)
        self.__table = {}

    def __call__(self, key: str = None, *, code: int = None):
        if code is None:
            code: int = next(self.counter)
        if key is not None:
            self.__table[code] = key
        return code

    def get_state(self, code: int):
        try:
            return self.__table[code]
        except KeyError:
            return None

class pineLexer:

    RE_FLAGS = re.UNICODE | re.VERBOSE

    state = StateGenerator(0)

    # BASIC ------------
    SKIP = state('SKIP')
    COMMENT = state('COMMENT')
    NEW_LINE = state('NEW_LINE')
    # ------------------

    # HTML TAGS ----
    HTML_0 = state('HTML_0')
    HTML_1 = state('HTML_1')
    HTML_2 = state('HTML_2')
    HTML = state('HTML')

    HEAD_0 = state('HEAD_0', code=HTML_0)
    HEAD_1 = state('HEAD_1')
    HEAD_2 = state('HEAD_2')
    HEAD = state('HEAD')

    BODY_0 = state('BODY_0')
    BODY_1 = state('BODY_1')
    BODY_2 = state('BODY_2')
    BODY = state('BODY')
    # --------------

    # INDENT ---------
    INDENT = state('INDENT')
    INDENT_0 = state('INDENT_0')
    INDENT_1 = state('INDENT_1')
    INDENT_2 = state('INDENT_2')
    INDENT_3 = state('INDENT_3', code=INDENT)
    # ----------------

    # PINE CODE -----------------------
    ## INCLUDE ------------------------
    PINE_INC = state('PINE_INC')
    PINE_INC_INDENT = state('PINE_INC_INDENT')
    PINE_INC_INDENT_0 = state('PINE_INC_INDENT_0')
    PINE_INC_INDENT_1 = state('PINE_INC_INDENT_1')
    PINE_INC_SKIP = state('PINE_INC_SKIP')
    PINE_INC_QUOTE_0 = state('PINE_INC_QUOTE_0')
    PINE_INC_QUOTE_TEXT = state('PINE_INC_QUOTE_TEXT')
    PINE_INC_QUOTE_1 = state('PINE_INC_QUOTE_1')
    PINE_INC_DOUBLEQUOTE_0 = state('PINE_INC_DOUBLEQUOTE_0')
    PINE_INC_DOUBLEQUOTE_TEXT = state('PINE_INC_DOUBLEQUOTE_TEXT')
    PINE_INC_DOUBLEQUOTE_1 = state('PINE_INC_DOUBLEQUOTE_1')
    # ---------------------------------

    ## VARIABLE -----------------------
    PINE_VAR = state('PINE_VAR')
    PINE_VAR_INDENT = state('PINE_VAR_INDENT')
    PINE_VAR_INDENT_0 = state('PINE_VAR_INDENT_0')
    PINE_VAR_INDENT_1 = state('PINE_VAR_INDENT_1')
    PINE_VAR_SKIP_0 = state('PINE_VAR_SKIP_0')
    PINE_VAR_NAME = state('PINE_VAR_NAME')
    PINE_VAR_SKIP_1 = state('PINE_VAR_SKIP_1')
    PINE_VAR_EQUAL = state('PINE_VAR_EQUAL')
    PINE_VAR_SKIP_2 = state('PINE_VAR_SKIP_2')
    PINE_VAR_QUOTE_0 = state('PINE_VAR_QUOTE_0')
    PINE_VAR_QUOTE_TEXT = state('PINE_VAR_QUOTE_TEXT')
    PINE_VAR_QUOTE_1 = state('PINE_VAR_QUOTE_1')
    PINE_VAR_DOUBLEQUOTE_0 = state('PINE_VAR_DOUBLEQUOTE_0')
    PINE_VAR_DOUBLEQUOTE_TEXT = state('PINE_VAR_DOUBLEQUOTE_TEXT')
    PINE_VAR_DOUBLEQUOTE_1 = state('PINE_VAR_DOUBLEQUOTE_1')
    # ---------------------------------

    # MARKDOWN -------------------
    ## DIV -----------------------
    MD_DIV_PUSH = state('MD_DIV_PUSH')
    MD_DIV_HEADER_SKIP_0 = state('MD_DIV_HEADER_SKIP_0')
    MD_DIV_HEADER_TAG = state('MD_DIV_HEADER_TAG')
    MD_DIV_HEADER_SKIP_1 = state('MD_DIV_HEADER_SKIP_1')
    MD_DIV_HEADER_ID = state('MD_DIV_HEADER_ID')
    MD_DIV_HEADER_SKIP_2 = state('MD_DIV_HEADER_SKIP_2')
    MD_DIV_HEADER_CLASS = state('MD_DIV_HEADER_CLASS')
    MD_DIV_HEADER_SKIP = state('MD_DIV_HEADER_SKIP')
    # A LOT HAPPENS HERE!
    MD_DIV_POP = state('MD_DIV_POP')
    ## ---------------------------

    ## LIST ----------------------
    MD_ULIST = state('MD_ULIST')
    MD_ULIST_SKIP = state('MD_ULIST_SKIP')
    # A LOT HAPPENS HERE!
    MD_OLIST = state('MD_OLIST')
    MD_OLIST_SKIP = state('MD_OLIST_SKIP')
    ## ---------------------------

    ## HEADERS ---------------
    MD_HEADER = state('MD_HEADER')
    MD_HEADER_NUMBER = state('MD_HEADER_NUMBER')
    ## -----------------------

    ## TEXT -------------------
    MD_TEXT = state('MD_TEXT')
    MD_TEXT_SKIP = state('MD_TEXT_SKIP')
    ### LINK & LOAD -----------
    MD_LINK_LOAD_PUSH = state('MD_LINK_LOAD_PUSH')
    MD_LINK_LOAD_HREF = state('MD_LINK_LOAD_HREF')
    MD_LINK_LOAD_POP = state('MD_LINK_LOAD_POP')
    ### LINK ------------------
    MD_LINK_STAR = state('MD_LINK_STAR')
    MD_LINK_PUSH = state('MD_LINK_PUSH')
    # A FEW HAPPENS HERE!
    MD_LINK_POP = state('MD_LINK_POP')
    ### LOAD ------------------
    MD_LOAD = state('MD_LOAD')
    MD_LOAD_TYPE = state('MD_LOAD_TYPE')
    ### VARIABLE ---------------
    MD_TEXT_VAR = state('MD_TEXT_VAR')
    MD_TEXT_VARNAME = state('MD_TEXT_VARNAME')
    ### EFFECTS ----------------
    MD_TEXT_I = state('MD_TEXT_I')
    MD_TEXT_B = state('MD_TEXT_B')
    MD_TEXT_C = state('MD_TEXT_C')
    MD_TEXT_S = state('MD_TEXT_S')
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
        HTML_0: { # HEAD_0 
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
        PINE_INC_INDENT:{
            r"[^\S\r\n]": PINE_INC_SKIP,
            r"\'": PINE_INC_QUOTE_0,
            r"\"": PINE_INC_DOUBLEQUOTE_0,
        },
        PINE_INC_INDENT_0:{
            r"\ ": PINE_INC_INDENT_1,
        },
        PINE_INC_INDENT_1:{
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

        },
        PINE_VAR_INDENT: {

        },
        PINE_VAR_INDENT_0: {

        },
        PINE_VAR_INDENT_1: {

        },
        PINE_VAR_SKIP_0: {

        },
        PINE_VAR_NAME: {

        },
        PINE_VAR_SKIP_1: {

        },
        PINE_VAR_EQUAL: {

        },
        PINE_VAR_SKIP_2: {

        },
        PINE_VAR_QUOTE_0: {

        },
        PINE_VAR_QUOTE_TEXT: {

        },
        PINE_VAR_QUOTE_1: {

        },
        PINE_VAR_DOUBLEQUOTE_0: {

        },
        PINE_VAR_DOUBLEQUOTE_TEXT: {

        },
        PINE_VAR_DOUBLEQUOTE_1: {

        },
        # ---------------------------------
    }

    def __init__(self, source: Source):
        self.source = source
        self.states = self.compile_states()
    
        self.flags = {}
        self.stack = []

    def parse(self):
        """"""
        queue = list(reversed(self.source))
        regex: re.Pattern

        c: int = 0
        r: int = self.NEW_LINE
        s: int

        while queue:
            char: str = queue.pop()
            for regex, s in self.states[r].items():
                if regex.match(char):
                    self.trans(r, s)
                    r = s
                    break
            else:
                raise SyntaxError("")
            c += 1
        else:
            self.eof()

    def eof(self):
        """"""
        print("EOF KKKK")

    def compile_states(self) -> dict:
        """"""
        states = {}
        trans: dict
        r: int
        s: int
        for r, trans in self._states.items():
            if r not in states:
                states[r] = {}
            for pattern, s in trans.items():
                regex = re.compile(pattern, self.RE_FLAGS)
                states[r][regex] = s

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
        print(f"{r} -> {s}")
