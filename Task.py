#!/usr/bin/env python

class Task (object):

    TYPE_TASK = "0"
    TYPE_ISR = "1"

    def __init__ (self, name, taskType, code):
        self._name = name
        self._type = taskType
        self._code = code

if __name__ == '__main__':
    pass
