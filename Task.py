#!/usr/bin/env python

class TaskExecution (object):
    def __init__ (self, timeIn, timeOut, core):
        self._timeIn = timeIn
        self._timeOut = timeOut
        self._core = core

    def getTimeIn (self):
        return self._timeIn

    def getTimeOut (self):
        return self._timeOut

    def getDuration (self):
        return (self._timeOut - self._timeIn)

    def getCore (self):
        return (self._core)

    def __str__ (self):

        return "core-" + str(self._core) + " " + str(self._timeIn) + ":" + \
            str(self._timeOut)

class Task (object):

    ALL_CORES = -1

    TYPE_TASK = "0"
    TYPE_ISR = "1"

    TYPE_NAME_TASK = "Task"
    TYPE_NAME_ISR = "Isr"

    TYPE_NAMES = {TYPE_TASK : TYPE_NAME_TASK,
                  TYPE_ISR : TYPE_NAME_ISR }

    def __init__ (self, name, taskType, code):
        self._name = name
        self._type = taskType
        self._code = code
        self._executions = []

    def __str__ (self):
        return self._name + "(" + self._code + ") " + \
            Task.TYPE_NAMES [self._type]

    def addExecution (self, e):
        self._executions.append (e)

    def getSummary (self, beginTime, endTime, core):
        """ This function returns the summary of the executions:
            * number of exections
            * percentage
            * total time 
            The core parameter can be a number or ALL_CORES """
        summary = {'number': 0, 'percentage': 0.0, 'duration': 0}

        for e in self._executions:
            if (core == Task.ALL_CORES) or ( core == e.getCore()):
                if (e.getTimeIn () >= beginTime) and (e.getTimeOut() <= endTime):
                    summary ['number'] += 1
                    summary ['duration'] += e.getDuration ()
        summary ['percentage'] = float (summary ['duration']) * 100.0 /\
                        float (endTime - beginTime)
        return summary 

class TaskList (object):
    def __init__ (self):
        self._tasks =[]

    def addTask (self, t): 
        self._tasks.append (t)

if __name__ == '__main__':
    T = Task ("tarea", Task.TYPE_TASK, "300304")
    T.addExecution (TaskExecution (20333, 32405, 2))
    T.addExecution (TaskExecution (18333, 19567, 1))

    print T.getSummary (10000, 50000, 1)
