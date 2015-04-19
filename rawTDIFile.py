#! /usr/bin/env python
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

"""
/*
 * Each entry is a multiple of 64-bits, the first 64 bits are formatted like the
 * following:
 *
 *                       24                      16                       8                       0
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |   CPU  |      TYPE    |                   ID                          |SR|     TS (38:32)     |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |                                         TS (31:0)                                             |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 *
 * Where:
 *    CPU  = is the cpu the event occured on (currently on 8 CPUs supported)
 *    TYPE = the type of the record, see below
 *    ID   = the Id of the record, it's value depends on the type
 *    SR   = Start record indicator, set to 1
 *    TS   = The timestamp of the record (39-bits)
 *
 *
 * IRQ and SoftIRQ Records
 * =======================
 *
 * These are just 64-bits in size and the ID field is set to indicate the
 * IRQ or SoftIRQ number
 *
 *
 * Task Records
 * ============
 *
 * Task records have an extra 128-bits after the header, the format is described
 * below.  The ID in the header is the task's pid.
 *
 *                       24                      16                       8                       0
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         COMM[0]       |        COMM[1]        |      COMM[2]          | 0|     COMM[3]        |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         COMM[4]       |        COMM[5]        |      COMM[6]          |        COMM[7]        |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         COMM[8]       |        COMM[9]        |      COMM[10]         | 0|     COMM[11]       |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         COMM[12]      |        COMM[13]       |                     TGID                      |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 *
 * Where:
 *    COMM = the first 14 characters of the task name. The second and tenth
 *           characters have their MSB set to zero (to ensure they don't
 *           accidently indicate a start or record).
 *    TGID = the task group identifier
 *
 *
 * uProbe and kProbe Records
 * =========================
 *
 * These are just 64-bits in size and the ID field is set to indicate the 
 * the ID or the kernel or user probe.
 *
 *
 *
 * Custom Events
 * =============
 *
 * The ID is specified by the user.  An extra 128-bits is appended that contains
 * a user supplied string describing the event
 *
 *                       24                      16                       8                       0
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         NAME[0]       |        NAME[1]        |      NAME[2]          | 0|     NAME[3]        |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         NAME[4]       |        NAME[5]        |      NAME[6]          |        NAME[7]        |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         NAME[8]       |        NAME[9]        |      NAME[10]         | 0|     NAME[11]       |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         NAME[12]      |        NAME[13]       |      NAME[14]         |        NAME[15]       |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 *
 * Where:
 *    NAME = 16 characters describing the event, the name must match for all
 *           events with the same ID (otherwise the UI gets confused). The
 *           fourth character has it's MSB set to zero (to ensure they don't
 *           accidently indicate a start or record).
 *
 *
 * Custom Events with Data / Values
 * =================================
 *
 * Basically the same as a normal custom event, but has an addition 64-bits
 * for storing an extra 4 characters of the name and a 32-bit data value.
 *
 *                       24                      16                       8                       0
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         NAME[0]       |        NAME[1]        |      NAME[2]          | 0|     NAME[3]        |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         NAME[4]       |        NAME[5]        |      NAME[6]          |        NAME[7]        |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |         NAME[8]       |        NAME[9]        |      NAME[10]         | 0|     NAME[11]       |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 * |                                           DATA / VALUE                                        |
 * +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 *
 *
 */"""

import sys
import os

class TimeDoctorEntry (object):
    
    def __init__ (self, cpu, cmd, ident, timestamp): 
        self._cpu = cpu
        self._cmd = cmd
        self._id = ident
        self._ts = timestamp
        self._div = 53597481.0 / 1000000000.0

    def __str__ (self):
        return "cmd: " + str(self._cmd) + " cpu: " + str(self._cpu) + " id: " + str(self._id) + \
            " timestamp: " + str (self._ts) \
        + " ts " + str(float (self._ts) * self._div)

    def getCpu (self):
        return self._cpu

    def getCmd (self):
        return self._cmd

    def getId (self):
        return self._id

    def getTimeStamp (self):
        return self._ts

class TaskAction (object):
    def __init__ (self, header, name, tgid, isEntry):
        self._header = header
        self._name =name
        self._tgid = tgid
        self._isEntry = isEntry

    def getHeader (self):
        return self._header

    def getName (self):
        return self._name

    def getTGID (self):
        return self._tgid

    def getTaskId (self):
        return str (self._header.getId ()) + str(self._tgid)

    def getIsEntry (self):
        return self._isEntry

    def __str__ (self):
        return str(self._header) + " name: " + self._name + " TGID: " + str(self._tgid)

class TaskEntry (TaskAction):
    def __init__ (self, header, name, tgid):
        TaskAction.__init__ (self, header, name, tgid, True)

    def __str__ (self):
        return "Task Entry " + TaskAction.__str__ (self)

class TaskExit (TaskAction):
    def __init__ (self, header, name, tgid):
        TaskAction.__init__ (self, header, name, tgid, False)

    def __str__ (self):
        return "Task Exit " + TaskAction.__str__ (self)

class Isr (object):
    # These are defined in the linux kernel
    SOFT_IRQ_NAMES = ['HI', 'TIMER', 'NET_TX', 'NET_RX', 'BLOCK', 
        'BLOCK_IOPOLL', 'TASKLET', 'SCHED', 'HRTIMER', 'RCU']

    def __init__ (self, header, hardIsr, soft, isEntry):
        self._header = header
        self._soft = soft
        self._isEntry = isEntry
        if soft:
            try:
                self._name = Isr.SOFT_IRQ_NAMES [self._header.getId ()]
            except:
                self._name = "Soft_IRQ_" + str (self._header.getId ()) 
        else:
            try:
                self._name = hardIsr [str(self._header.getId ())]
            except:
                self._name = "IRQ_" + str (self._header.getId ()) 

    def getIsSoft (self):
        return self._soft

    def getHeader (self):
        return self._header

    def getName (self):
        return self._name

    def getTaskId (self):
        return "IRQ_" + str(self._header.getId ())

    def getIsEntry (self):
        return self._isEntry

    def __str__ (self):
        retVal = str (self._header)
        if self._name:
            retVal += " name: " + self._name
        return retVal

class IsrEntry (Isr):
    def __init__ (self, header, hardIsr, soft):
        Isr.__init__ (self, header, hardIsr, soft, True)

    def __str__ (self):
        beginning = ""
        if self._soft:
            beginning = "Soft "
        return beginning + "Isr Entry " + Isr.__str__ (self)

class IsrExit (Isr):
    def __init__ (self, header, hardIsr, soft):
        Isr.__init__ (self, header, hardIsr, soft, False)

    def __str__ (self):
        beginning = ""
        if self._soft:
            beginning = "Soft "
        return beginning + "Isr Exit " + Isr.__str__ (self)

class rawTDIFile (object):

    TD_CMD_NULL                  = 0

    TD_CMD_TASK_CREATE           = 1
    TD_CMD_TASK_DESTROY          = 2

    TD_CMD_TASK_ENTRY            = 3
    TD_CMD_TASK_EXIT             = 4

    TD_CMD_ISR_ENTRY             = 5
    TD_CMD_ISR_EXIT              = 6
    TD_CMD_SOFTIRQ_ENTRY         = 7
    TD_CMD_SOFTIRQ_EXIT          = 8

    TD_CMD_EVENT_ENTRY           = 9
    TD_CMD_EVENT_EXIT            = 10
    TD_CMD_EVENT_SINGLE          = 11

    TD_CMD_EVENT_SINGLE_DATA     = 12
    TD_CMD_VALUE                 = 13

    TD_CMD_UPROBE_ENTRY          = 14
    TD_CMD_UPROBE_EXIT           = 15
    TD_CMD_UPROBE_SINGLE         = 16
    TD_CMD_KPROBE_ENTRY          = 17
    TD_CMD_KPROBE_EXIT           = 18
    TD_CMD_KPROBE_SINGLE         = 19

    TD_CMD_TASK_MIGRATE          = 20

    TD_CMD_LAST                  = 21

    HARD_ISR_FILE = "cat_proc_interrupts.txt"


    def __init__ (self):
        self._firsTime = None

    def processHeader (self, block_bytes):

        block_bytes = bytearray (block_bytes)

        firstWord = (block_bytes [3] << 24) | (block_bytes[2] << 16) |\
                    (block_bytes[1] << 8) | block_bytes[0]

        cpu = (firstWord & 0xe0000000) >> 29
        cmd = (firstWord & 0x1f000000) >> 24
        id = (firstWord & 0x00ffff00) >> 8
        ts = firstWord & 0x7f 

        secondWord = (block_bytes [7] << 24) | (block_bytes[6] << 16) |\
                    (block_bytes[5] << 8) | block_bytes[4]
        ts = ts << 32 | secondWord

        if self._firsTime == None:
            self._firsTime = ts
            ts= 0
        else:
            ts = ts - self._firsTime

        return TimeDoctorEntry (cpu, cmd, id, ts)

    def processTask (self, fp):
        block = fp.read (16)
        block = bytearray (block)
        bytes_in_name = bytearray ()
        for b in block [:12] + block [14:]:
            if b != 0:
                bytes_in_name.append (b)
            else:
                break
        name = str(bytes_in_name)
        tgid = int (block [12] << 8 | block [14])
        return name, tgid

    def processTaskEntry (self, fp, header):
        name, tgid = self.processTask (fp)
        return TaskEntry (header, name, tgid)

    def processTaskExit (self, fp, header):
        name, tgid = self.processTask (fp)
        return TaskExit (header, name, tgid)

    def processIsrEntry (self, fp, header, soft = False):
        return IsrEntry (header, self._hardIsr, soft)

    def processIsrExit (self, fp, header, soft=False):
        return IsrExit (header, self._hardIsr, soft)

    def readHardIsr (self, fileName):
        # We try to find a HARD_ISR_FILE in the same folder as the raw file
        self._hardIsr = {}

        path = os.path.join(os.path.dirname (os.path.abspath (fileName)), 
                rawTDIFile.HARD_ISR_FILE)

        if os.path.isfile (path):
            fp = open (path, "r")
            for line in fp:
                line = line.strip ()
                pos = line.find ("GIC")
                if pos > -1:
                    parts = line.split (' ')
                    self._hardIsr [parts[0][:-1]] =  parts[-1].strip ()
            fp.close ()


    def readRawFile (self, fileName, cbFunction):
        consecutiveErrors = 0
        self.readHardIsr (fileName)
        fp = open (fileName, "rb")

        block = fp.read (8)
        while len (block) == 8:
            T = None
            header = self.processHeader (block)
            if header.getCmd() == rawTDIFile.TD_CMD_TASK_ENTRY:
                T = self.processTaskEntry (fp, header)
            elif header.getCmd () == rawTDIFile.TD_CMD_TASK_EXIT:
                T = self.processTaskExit (fp, header)
            elif header.getCmd () == rawTDIFile.TD_CMD_ISR_ENTRY:
                T = self.processIsrEntry (fp, header)
            elif header.getCmd () == rawTDIFile.TD_CMD_ISR_EXIT:
                T = self.processIsrExit (fp, header)
            elif header.getCmd () == rawTDIFile.TD_CMD_SOFTIRQ_ENTRY:
                T = self.processIsrEntry (fp, header, True)
            elif header.getCmd () == rawTDIFile.TD_CMD_SOFTIRQ_EXIT:
                T = self.processIsrExit (fp, header, True)
            else:
                print "Unkown cmd " + str(header.getCmd ())
                consecutiveErrors += 1

            if T:
                cbFunction (T)
                consecutiveErrors = 0

            if consecutiveErrors > 5:
                # This does not look as a raw file
                print "Too many consecutive errors. Invalid file. "
                return -1

            block = fp.read(8)
        
        return (0)


if __name__ == '__main__':
    def cbFunction (task):
        print ">> " + str(task)

    R = rawTDIFile ()
    retVal = R.readRawFile (sys.argv[1], cbFunction)
    sys.exit (retVal)
