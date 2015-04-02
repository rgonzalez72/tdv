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

    def clone (self):
        return TaskExecution (self._timeIn, self._timeOut, self._core)

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
        self._number = 0
        self._total = 0
        self._percentage = 0.0
        self._selected = True

    def clone (self):
        T = Task (self._name, self._type, self._code)
        T._number = self._number
        T._total = self._total
        T._percentage = self._percentage
        T._selected = self._selected
        for e in self._executions:
            T.addExecution (e.clone ())
        return T

    def __str__ (self):
        return self._name + "(" + self._code + ") " + \
            Task.TYPE_NAMES [self._type]

    def addExecution (self, e):
        self._executions.append (e)
        self._number += 1
        self._total += e.getDuration ()

    def calcPercentage (self, beginTime, endTime):
        self._percentage =  float (self._total) * 100.0 /\
                        float (endTime - beginTime)

    def getNumber (self):
        return self._number

    def getTotalDuration (self):
        return self._total

    def getPercentage (self):
        return self._percentage

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

    def getSelected (self):
        return self._selected

    def setSelected (self, selected):
        self._selected = selected

class TaskList (object):
    def __init__ (self):
        self._tasks =[]
        self._lastTime = 0
        self._numCores = 0

    def clone (self):
        TL = TaskList ()
        TL._lastTime = self._lastTime
        TL._numCores = self._numCores
        for t in self._tasks:
            TL._tasks.append (t.clone ())
        return TL

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
                self._numCores += 1
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

    def calcPercentage (self):
        for T in self._tasks:
            T.calcPercentage (0, self._lastTime)

    def sortByName (self, reverse=False):
        self._tasks = sorted (self._tasks, reverse = reverse)

    def sortByType (self, reverse=False):
        self._tasks =sorted (self._tasks, key=lambda k: k.getTypeName (),
                reverse = reverse)

    def sortByNumber (self, reverse=False):
        self._tasks =sorted (self._tasks, key=lambda k: k.getNumber (),
                reverse = reverse)

    def sortByExecutionTime (self, reverse=False):
        self._tasks =sorted (self._tasks, key=lambda k: k.getTotalDuration (),
                reverse = reverse)

    def getNumberOfTasks (self):
        return len (self._tasks)

    def getTask (self, index):
        return self._tasks[index]

    def getNumEnabled (self):
        enabled = 0
        for t in self._tasks:
            if t.getSelected ():
                enabled += 1
        return enabled

    def getNumberOfCores (self):
        return self._numCores

if __name__ == '__main__':
    T = TaskList ()
    T.readTDFile (sys.argv[1])

    for t in T._tasks:
        S = t.getSummary (0, T.getLastTime(), Task.ALL_CORES)
        print t
        print S
    print len (T._tasks)
