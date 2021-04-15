import re
import itertools as it
from dataclasses import asdict
from collections import deque

from cstream import stdwar, stderr, stdlog

from ..pinelib import Source
from ..items import mdType, mdNull, mdHTML, mdItalic, mdBold, mdStrike, mdCode

from .expgrammar import (
    states as exp_states,
    transitions as exp_transitions,
    state,
    transition,
    NEW_LINE,
    Flags,
)


class Stack(object):
    def __init__(self):
        self._stack = []

    def __str__(self):
        return "\n".join(["[TOP]", *map(repr, reversed(self._stack)), "[BOT]"])

    def __bool__(self):
        return bool(self._stack)

    @property
    def top(self):
        if len(self._stack) > 0:
            return self._stack[-1]
        else:
            return None

    def clear(self):
        self._stack.clear()

    def push(self, item: object):
        self._stack.append(item)

    def pop(self):
        if len(self._stack) > 0:
            return self._stack.pop()
        else:
            return None


class CharStack(Stack):
    def flush(self) -> str:
        s = "".join(self._stack)
        self._stack.clear()
        return s

    def __str__(self):
        return "[" + "".join(map(repr, self._stack)) + "]"


def todo():
    raise NotImplementedError()


class pineParser:

    state = state
    transition = transition

    RE_FLAGS = re.UNICODE | re.VERBOSE

    def __init__(self, source: Source, *, ensure_html: bool = False, debug: bool = False):
        self.ensure_html = bool(ensure_html)
        self.debug = debug
        self.source = source
        self.transitions = self.compile_transitions(exp_transitions)
        self.states = self.compile_states(exp_states)

        self.flags = Flags()
        self.table = {}
        self.stack = Stack()
        self.tag_stack = Stack()
        self.char_buffer = CharStack()

    def get_var(self, key: str):
        try:
            return self.table[key]
        except KeyError:
            return mdNull()

    def set_var(self, key: str, value: str):
        self.table[key] = value

    def test(self, *args, **kwargs):
        ...

    def parse(self, *, ensure_html: bool = False):
        """"""
        try:
            self.ensure_html = bool(ensure_html)

            ## Clear Parser Stack
            self.stack.clear()

            queue = ["\n", *reversed(self.source)]
            regex: re.Pattern

            self.c: int = 0
            self.r: int = NEW_LINE
            self.s: int
            T: list

            while queue:
                self.char: str = queue.pop()

                next_char = False
                while next_char is not True:
                    for regex, s, T in self.states[self.r]:
                        if regex is None or regex.match(self.char):
                            next_char = self.trans(self.r, s, T, self.char)
                            self.r = s
                            break
                    else:
                        self.syntax_error()
                self.c += 1
            else:
                self.eof()
        except Exception as err:
            stdlog[0] << self.env
            stderr[0] << err

    def include(self, path: str):
        """"""
        stdlog[0] << f"INCLUDE '{path}'"

    def syntax_error(self, *args, **kwargs):
        lexinfo: dict = self.source.lexchr(self.c)

        stderr[0] << f"In '{self.source.fpath}' at line {lexinfo['lineno']}:\n"
        stderr[0] << f"{self.source.lines[lexinfo['lineno']]}\n"
        stderr[0] << f"{' ' * lexinfo['chrpos']}^\n"
        stderr[
            0
        ] << f"Syntax Error in char '{self.char}', state '[{self.r}]{self.state.get_state(self.r)}'.\n"

        raise SyntaxError()

    def eof(self):
        """"""
        if not self.check_flags():
            stderr[0] << "Unexpected EOF."
        else:
            stdlog[0] << self.env

    @property
    def env(self):
        return (
            "EOF KKKK EAE MAN"
            f"TABLE:\n{self.table}\n"
            f"STACK:\n{self.stack}\n"
            f"CHAR BUFFER:\n{self.char_buffer}\n"
            f"FLAGS:\n{asdict(self.flags)}"
        )

    def check_flags(self):
        return not (self.flags.i or self.flags.b or self.flags.s or self.flags.c)

    def compile_transitions(self, transitions: dict) -> dict:
        return transitions.copy()

    def compile_states(self, raw_states: dict) -> dict:
        """"""
        states = {}
        trans: dict
        r: int
        s: int
        t: int

        missing = set()

        for r, trans in raw_states.items():
            if r not in states:
                states[r] = []
            if not trans:
                stdwar[0] << (
                    f"Warning: state '{state.get_state(r)}' ({r}) is a dead end."
                )
            for pattern, (s, T) in trans.items():
                if pattern is None:
                    regex = None
                else:
                    regex = re.compile(pattern, self.RE_FLAGS)
                for t in T:
                    if t not in self.transitions:
                        missing.add(t)
                states[r].append((regex, s, T))
                state.activate(s)

        for t in missing:
            stdwar[0] << f"Transition '{transition.get_state(t)}' not implemented."

        for s in state.inactive():
            stdwar[0] << (
                f"Warning: state '{state.get_state(s)}' ({s}) is unreachable."
            )

        return states

    def trans_debug(self, r: int, s: int, char: str = None):
        """"""
        if char is None:
            print(f"{self.state.get_state(r)} -> {self.state.get_state(s)}")
        else:
            print(f"{char!r} : {self.state.get_state(r)} -> {self.state.get_state(s)}")
        if s == 0:
            print()

    def trans(self, r: int, s: int, T: list, char: str) -> bool:
        """Transition from state r to s.

        Parameters
        ----------
        r : int
            Current state.
        s : int
            Next state.
        T: list[int]
            Transition actions.
        char : str
            Last character from input.

        Returns
        -------
        bool
            Wether to pop a new char from source or not.
        """
        if self.debug: self.trans_debug(r, s, char)

        for t in T:
            if t is None:
                return False
            elif t not in self.transitions:
                raise SystemError(
                    f"Transition '[{t}]{transition.get_state(t)}' is not available."
                )
            else:
                self.transitions[t](self, char)
        else:
            return True