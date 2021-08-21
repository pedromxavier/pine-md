from collections import deque

class Stack(object):

    def __init__(self, buffer: list = None):
        self.__stack = deque(buffer if buffer else [])

    def __bool__(self) -> bool:
        return bool(self.__stack)

    def push(self, x: object):
        self.__stack.append(x)

    def pop(self) -> object:
        if self.__stack:
            return self.__stack.pop()
        else:
            return None

    @property
    def top(self) -> object:
        if self.__stack:
            return self.__stack[-1]
        else:
            return None

    