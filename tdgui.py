#!/usr/bin/python

import wx
from wx.lib import sheet
import sys
import Task

class TDGUI (wx.Frame):
    def __init__ (self, parent, id, title, tdiFile):
        wx.Frame.__init__ (self, parent, id, title, size= (800, 600))

        self.statusbas = self.CreateStatusBar ()
        self.CreateMenuBar ()

        self.graphics = TaskGrid (self, tdiFile)
        self.graphics.SetFocus ()
        
        
        self.Centre ()
        self.Show (True)

    def CreateMenuBar (self):
        menubar = wx.MenuBar ()
        filem = wx.Menu ()
        helpm = wx.Menu ()

        Oitem = filem.Append (wx.ID_FILE, "&Open", "Open TD file")
        Qitem = filem.Append (wx.ID_EXIT, "&Quit", "Quit application")
        menubar.Append (filem, "&File")
        menubar.Append (helpm, "&Help")
        Aitem = helpm.Append (wx.ID_HELP, "&About", "About")

        self.SetMenuBar (menubar)

        self.Bind (wx.EVT_MENU, self.OnQuit, Qitem)
        self.Bind (wx.EVT_MENU, self.OnAbout, Aitem)
        self.Bind (wx.EVT_MENU, self.OnOpenFile, Oitem)

    def OnQuit (self, e):
        self.Close ()

    def OnAbout (self, e):
        A = AboutDialog (self, wx.ID_ANY, "About TDV") 
        A.Centre ()
        A.ShowModal ()

    def OnOpenFile (self, e):
        print "OnOpenFile"

class AboutDialog (wx.Dialog):
    def __init__ (self, parent, id, title):
        wx.Dialog.__init__ (self, parent, id, title)

        vbox = wx.BoxSizer (wx.VERTICAL)
        hbox0 = wx.BoxSizer (wx.HORIZONTAL)
        hbox2 = wx.BoxSizer (wx.HORIZONTAL)
        hbox3 = wx.BoxSizer (wx.HORIZONTAL)

        panel = wx.Panel (self, wx.ID_ANY)

        label1 = wx.StaticText (panel, wx.ID_ANY, 
                "An application for visualizing time doctor files.")
        hbox1.Add (label1, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)

        self.btnClose = wx.Button (panel, wx.ID_CLOSE, "&Close")
        hbox3.Add (self.btnClose, 0, wx.CENTER, 20)
        self.Bind (wx.EVT_BUTTON, self.OnClose, self.btnClose)

        vbox.Add (hbox0, 0, wx.EXPAND)
        vbox.Add (hbox1, 0, wx.LEFT)
        vbox.Add (hbox2, 0, wx.LEFT)
        vbox.Add (hbox3, 0, wx.CENTER)

        panel.SetSizer(vbox)
        minSize = vbox.GetMinSize()
        height = minSize.GetHeight ()
        minSize.SetHeight (height + 60)
        self.SetSize (minSize )

    def OnClose (self, e):
        self.Close ()

class TaskGrid (sheet.CSheet):
    def __init__ (self, parent, tdiFile):
        sheet.CSheet.__init__ (self, parent)

        self._taskList = Task.TaskList ()
        self._taskList.readTDFile (tdiFile)
        self._taskList.sortByName ()

        self._numRows = self._taskList.getNumberOfTasks ()
        self._numCols = 5
        self.SetNumberRows (self._numRows)
        self.SetNumberCols (self._numCols)

        self.SetColLabelValue (0, "Type")
        self.SetColLabelValue (1, "Number")
        self.SetColLabelValue (2, "Percentage")
        self.SetColLabelValue (3, "Accumulated time")
        self.SetColLabelValue (4, "Show")

        self.SetRowLabelSize (150)
        self.SetColSize (0, 60)
        self.SetColSize (1, 80)
        self.SetColSize (2, 100)
        self.SetColSize (3, 200)
        self.SetColSize (4, 60)

        self._enabled = []
        for i in range (self._numRows):
            T = self._taskList.getTask (i)
            self.SetRowLabelAlignment (i, wx.LEFT)
            self.SetRowLabelValue (i, T.getName ())

            self.SetCellValue (i, 0, T.getTypeName ())

            S = T.getSummary (0, self._taskList.getLastTime (), Task.Task.ALL_CORES)
            self.SetCellValue (i, 1, str (S['number']))
            self.SetCellValue (i, 2, str (S['percentage']) + " %")
            self.SetCellValue (i, 3, str (S['duration']))
            self.EnableRow (i, True)

        self.Bind (wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelClick)

    def EnableRow (self, row, enable):
        if len (self._enabled) <= row:
            self._enabled.append (False)

        if enable:
            self.SetCellValue (row, 4, "Yes")
            self._enabled [row] = True
        else:
            self.SetCellValue (row, 4, "No")
            self._enabled [row] = False

        for i in range (self._numCols):
            if enable:
                self.SetCellBackgroundColour (row, i, "#C0ffC0")
            else:
                self.SetCellBackgroundColour (row, i, "#ffC0C0")
            
    def OnLabelClick (self, event):
        row = event.GetRow()
        col = event.GetCol()

        if row == -1 and col == -1:
            pass
        if row == -1:
            pass
        else:
            # toggle row
            self.EnableRow (row, not self._enabled[row])

#event.Skip ()

app = wx.App ()
TDGUI (None, -1, "Time Doctor GUI", sys.argv[1])
app.MainLoop ()
