#!/usr/bin/env python

################################################################################
#  Copyright (C) 2015  Rodolfo Gonzalez <rgonzalez72@yahoo.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################


import sys
import rawTDIFile

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
    TYPE_AGENT = "8"

    TYPE_NAME_TASK = "Task"
    TYPE_NAME_ISR = "Isr"
    TYPE_NAME_AGENT = "Agent"

    TYPE_NAMES = {TYPE_TASK : TYPE_NAME_TASK,
                  TYPE_ISR : TYPE_NAME_ISR,
                  TYPE_AGENT : TYPE_NAME_AGENT, }

    CORES_MAP = [
        0x00000001,
        0x00000002,
        0x00000004,
        0x00000008,
        0x00000010,
        0x00000020,
        0x00000040,
        0x00000080,
        0x00000100,
        0x00000200,
        0x00000400,
        0x00000800,
        0x00001000,
        0x00002000,
        0x00004000,
        0x00008000,
        0x00010000,
        0x00020000,
        0x00040000,
        0x00080000,
        0x00100000,
        0x00200000,
        0x00400000,
        0x00800000,
        0x01000000,
        0x02000000,
        0x04000000,
        0x08000000,
        0x10000000,
        0x20000000,
        0x40000000,
        0x80000000
    ]

    def __init__ (self, name, taskType, code):
        self._name = name
        self._type = taskType
        self._code = code
        self._executions = []
        self._number = 0
        self._total = 0
        self._percentage = 0.0
        self._selected = True
        self._cores = 0x00000000 # A 32 bitmap
        self._lastStart = None

    def clone (self):
        T = Task (self._name, self._type, self._code)
        T._number = self._number
        T._total = self._total
        T._percentage = self._percentage
        T._selected = self._selected
        T._cores = self._cores
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
        self._cores = self._cores | Task.CORES_MAP [e.getCore()]

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
        if type (other) is Task:
            return self._code == other._code
        else:
            return False

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

    def getCores (self):
        return self._cores

    def getCoreList (self):
        coreList = []
        for i in range (len(Task.CORES_MAP)):
            if self._cores & Task.CORES_MAP[i] != 0x00000000:
                coreList.append (i)
        return coreList

    def getCoreString (self):
        l = self.getCoreList ()
        coreStr = ""
        for c in l:
            coreStr += str(c) + " "
        return coreStr

    def getLastStart (self):
        return self._lastStart

    def setLastStart (self, lastStart):
        self._lastStart = lastStart

    def resetLastStart (self):
        self._lastStart = None

class TaskList (object):
    def __init__ (self):
        self._tasks =[]
        self._lastTime = 0
        self._numCores = 0
        self._filename = ""
        self._speed = 0

    def clone (self):
        TL = TaskList ()
        TL._lastTime = self._lastTime
        TL._numCores = self._numCores
        TL._filename = self._filename
        TL._speed = self._speed
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
        self._filename = fileName
        fp = open (fileName, "r")
        self._lastTime = 0
        currentCore = -1
        self._speep = 0
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
                if self._speed == 0 or currentCore == -1:
                    return -1
                parts = line.strip ().split (" ")
                stTime = float (parts[3]) * self._speed
                code = parts[2]
                T = self.findTaskByCode (code)
                T.setLastStart (stTime)
            elif line.startswith ("STO"):
                if self._speed == 0 or currentCore == -1:
                    return -1
                parts = line.strip ().split (" ")
                endTime = float (parts[3]) * self._speed
                code = parts[2]
                T = self.findTaskByCode (code)
                if T.getLastStart () != None:
                    E = TaskExecution (T.getLastStart(), endTime , currentCore)
                    T.addExecution (E)
                    T.resetLastStart ()
                if endTime > self._lastTime:
                    self._lastTime = endTime
            elif line.startswith ("SPEED"):
                parts = line.strip ().split (" ")
                
                # Units are nanoseconds
                self._speed = 1000000000.0 /float (parts[1])
            
        if self._speed == 0 or currentCore == -1 or len(self._tasks) <1:
            return -1
        else:
            return 0

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

    def sortByCores (self, reverse=False):
        self._tasks =sorted (self._tasks, key=lambda k: k.getCores (),
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

    def getFileName (self):
        return self._filename

    def getSpeed (self):
        return self._speed 

    def getTimeFormatted (self, t):
        # Convert to seconds and add the units
        return "%1.03lf s" % (t / 1000000000.0)

    def isAnyTaskSelected (self):
        anySel = False
        for t in self._tasks:
            if t.getSelected ():
                anySel = True
                break
        return anySel


    def processRawTask (self, task):
        cpu = task.getHeader ().getCpu ()
        timestamp = task.getHeader ().getTimeStamp ()
        if cpu >= self._numCores:
            self._numCores = cpu +1

        if timestamp > self._lastTime:
            self._lastTime = timestamp

        taskType = None
        isEntry = None
        if (type (task) is rawTDIFile.TaskEntry ):
            taskType = Task.TYPE_TASK
            isEntry = True
        elif (type (task) is rawTDIFile.TaskExit):
            taskType = Task.TYPE_TASK
            isEntry = False
        elif (type (task) is rawTDIFile.IsrEntry ):
            isEntry = True 
            if task.getIsSoft ():
                taskType = Task.TYPE_ISR
            else:
                taskType = Task.TYPE_AGENT
        elif (type (task) is rawTDIFile.IsrExit):
            isEntry = False 
            if task.getIsSoft ():
                taskType = Task.TYPE_ISR
            else:
                taskType = Task.TYPE_AGENT

        if taskType != None:
            # Check is the task already exits
            theTask = self.findTaskByCode (task.getTaskId ())
            if theTask == None:
                theTask = Task (task.getName (), taskType, task.getTaskId())
                self._tasks.append (theTask)

            if isEntry:
                theTask.setLastStart (task.getHeader().getTimeStamp ())
            else:
                staTime = theTask.getLastStart ()
                # At the start of the file we may have stop with no start
                if staTime != None:
                    E = TaskExecution (staTime, 
                            task.getHeader().getTimeStamp () ,
                            task.getHeader().getCpu())
                    theTask.addExecution (E)
                    theTask.resetLastStart ()
        else:
            print "Unexpected task type!!!"
            
                

    def readRawFile (self, fileName):
        self._tasks =[]
        self._lastTime = 0
        self._numCores = 0
        self._filename = fileName
        self._speed = 1 # Not really relevant here
        # A list of started tasks
        self._rawStatus = []
        R = rawTDIFile.rawTDIFile ()
        retVal = R.readRawFile (fileName, self.processRawTask)

        print "Last time " + str(self._lastTime)
        print "Num cores " + str(self._numCores)
        print "Speed " + str(self._speed)
        print "Num tasks " + str(len(self._tasks))

        return retVal

    def readFile (self, fileName):
        # Determine the type of file and 0 if ok -1 is invalid 
        retVal = -1

        try:
            retVal = self.readTDFile (fileName)
        except:
            pass
        
        if retVal != 0:
#try:
            retVal = self.readRawFile (fileName)
#            except:
#                pass

        return retVal

if __name__ == '__main__':
    T = TaskList ()
    if T.readFile (sys.argv[1]) == 0:
        for t in T._tasks:
            S = t.getSummary (0, T.getLastTime(), Task.ALL_CORES)
            print t
            print S
        print len (T._tasks)
