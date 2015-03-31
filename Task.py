#!/usr/bin/env python
import sys

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
    TYPE_OTRO = "8"

    TYPE_NAME_TASK = "Task"
    TYPE_NAME_ISR = "Isr"
    TYPE_NAME_OTRO = "Otro"

    TYPE_NAMES = {TYPE_TASK : TYPE_NAME_TASK,
                  TYPE_ISR : TYPE_NAME_ISR,
                  TYPE_OTRO : TYPE_NAME_OTRO, }

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
        self._summary = summary
        return self._summary 

    def __eq__ (self, other):
        return self._code == other._code

    def __bt__ (self, other):
        return self._name.lower () > other._name.lower ()

    def __be__ (self, other):
        return self._name.lower () >= other._name.lower ()

    def __lt__ (self, other):
        return self._name.lower () < other._name.lower ()

    def __le__ (self, other):
        return self._name.lower () <= other._name.lower ()

    def getCode (self):
        return self._code

    def getName (self):
        return self._name

    def getTypeName (self):
        return Task.TYPE_NAMES [self._type]

class TaskList (object):
    def __init__ (self):
        self._tasks =[]
        self._lastTime = 0

    def addTask (self, t): 
        self._tasks.append (t)

    def findTaskByCode (self, code):
        theTask = None
        for T in self._tasks:
            if T.getCode () == code:
                theTask = T
                break
        return theTask

    def readTDFile (self, fileName):
        fp = open (fileName, "r")
        self._lastTime = 0
        currentCore = 0
        for line in fp:
            if line.startswith ("CPU"):
                pos = line.find ("-")
                currentCore = int (line.strip () [pos+1])
            elif line.startswith ("NAM"):
                parts = line.strip ().split (" ")
                T = Task (parts[3], parts[1], parts[2])
                if not T in self._tasks:
                    self._tasks.append (T)
            elif line.startswith ("STA"):
                parts = line.strip ().split (" ")
                stTime = int (parts[3])
            elif line.startswith ("STO"):
                parts = line.strip ().split (" ")
                endTime = int (parts[3])
                code = parts[2]
                T = self.findTaskByCode (code)
                E = TaskExecution (stTime, endTime, currentCore)
                T.addExecution (E)
                if endTime > self._lastTime:
                    self._lastTime = endTime
            

    def getLastTime (self):
        return self._lastTime


    def sortByName (self):
        self._tasks = sorted (self._tasks)

    def sortByExecutionTime (self):
        # TODO
        pass

    def getNumberOfTasks (self):
        return len (self._tasks)

    def getTask (self, index):
        return self._tasks[index]

if __name__ == '__main__':
    T = TaskList ()
    T.readTDFile (sys.argv[1])

    for t in T._tasks:
        S = t.getSummary (0, T.getLastTime(), Task.ALL_CORES)
        print t
        print S
    print len (T._tasks)
