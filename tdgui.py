#!/usr/bin/python

import wx
from wx.lib import sheet
import sys
import Task

class TDGUI (wx.Frame):
    def __init__ (self, parent, id, title, tdiFile):
        wx.Frame.__init__ (self, parent, id, title, size= (800, 600))
        self.SetIcon (wx.Icon ('tdv.ico', wx.BITMAP_TYPE_ICO))

        self.statusbas = self.CreateStatusBar ()
        self.CreateMenuBar ()

        vbox = wx.BoxSizer (wx.VERTICAL)
        hbox0 = wx.BoxSizer (wx.HORIZONTAL)
        hbox1 = wx.BoxSizer (wx.HORIZONTAL)

        self.notebook = wx.Notebook (self, wx.ID_ANY, style= wx.RIGHT)

        sheet1 = TaskGrid (self.notebook, tdiFile)
        sheet1.SetFocus ()
        self._sheets = []
        self._sheets.append (sheet1)
        self._currentSheet = 0

        self.notebook.AddPage (sheet1, tdiFile)
        

        self.btnSelAll = wx.Button (self, wx.ID_ANY, "&Select All")
        self.btnUnselAll = wx.Button (self, wx.ID_ANY, "&Unselect All")
        self.btnShow = wx.Button (self, wx.ID_ANY, "&Show")

        vbox.Add (self.notebook, 1, wx.EXPAND)

        hbox1.Add (self.btnSelAll, 0, wx.CENTER | wx.RIGHT, 20)
        hbox1.Add (self.btnUnselAll, 0, wx.CENTER, 20)
        hbox1.Add (self.btnShow, 0, wx.CENTER | wx.LEFT, 20)
        
        vbox.Add ((5,5) , 0)
        vbox.Add (hbox1, 0, wx.CENTER)
        self.SetSizer(vbox)

        self.Bind (wx.EVT_BUTTON, self.OnSelectAll, self.btnSelAll)
        self.Bind (wx.EVT_BUTTON, self.OnUnselectAll, self.btnUnselAll)
        self.Bind (wx.EVT_BUTTON, self.OnShow, self.btnShow)
        
        self.Centre ()
        self.Show (True)

    def CreateMenuBar (self):
        menubar = wx.MenuBar ()
        filem = wx.Menu ()
        helpm = wx.Menu ()

        Oitem = filem.Append (wx.ID_FILE, "&Open", "Open TD file")
        Citem = filem.Append (wx.ID_CLOSE, "&Close", "Close curret file")
        Qitem = filem.Append (wx.ID_EXIT, "&Quit", "Quit application")
        menubar.Append (filem, "&File")
        menubar.Append (helpm, "&Help")
        Aitem = helpm.Append (wx.ID_HELP, "&About", "About")

        self.SetMenuBar (menubar)

        self.Bind (wx.EVT_MENU, self.OnQuit, Qitem)
        self.Bind (wx.EVT_MENU, self.OnAbout, Aitem)
        self.Bind (wx.EVT_MENU, self.OnOpenFile, Oitem)
        self.Bind (wx.EVT_MENU, self.OnCloseFile, Citem)

    def OnQuit (self, e):
        self.Close ()

    def OnAbout (self, e):
        A = AboutDialog (self, wx.ID_ANY, "About TDV") 
        A.Centre ()
        A.ShowModal ()

    def OnOpenFile (self, e):
        print "OnOpenFile"

    def OnCloseFile (self, e):
        print "OnCloseFile"

    def OnSelectAll (self, e):
        self._sheets [self._currentSheet].SelectAll ()

    def OnUnselectAll (self, e):
        self._sheets [self._currentSheet].UnselectAll ()

    def OnShow (self, e):
        title = "Showing " + self._sheets [self._currentSheet].getTdiFile ()
        S = ShowDialog (self, title)
        S.Centre ()
        S.Show ()

class AboutDialog (wx.Dialog):
    def __init__ (self, parent, id, title):
        wx.Dialog.__init__ (self, parent, id, title)

        vbox = wx.BoxSizer (wx.VERTICAL)
        hbox0 = wx.BoxSizer (wx.HORIZONTAL)
        hbox1 = wx.BoxSizer (wx.HORIZONTAL)
        hbox2 = wx.BoxSizer (wx.HORIZONTAL)
        hbox3 = wx.BoxSizer (wx.HORIZONTAL)

        panel = wx.Panel (self, wx.ID_ANY)

        label1 = wx.StaticText (panel, wx.ID_ANY, 
                "An application for visualizing time doctor files.")
        hbox0.Add (label1, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)

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
        self._taskList.calcPercentage ()
        self._taskList.sortByName ()
        self._tdiFile = tdiFile

        self._numRows = self._taskList.getNumberOfTasks ()
        self._numCols = 5
        self.SetNumberRows (self._numRows)
        self.SetNumberCols (self._numCols)
        self.setReverseCols ()
        self._reverseCols [0] = True

        self.EnableEditing (False)
        self.EnableCellEditControl (False)

        self.SetColLabelValue (0, "Type")
        self.SetColLabelValue (1, "Number")
        self.SetColLabelValue (2, "Percentage")
        self.SetColLabelValue (3, "Accumulated time")
        self.SetColLabelValue (4, "Show")

        self.SetRowLabelSize (150)
        self.SetColSize (0, 60)
        self.SetColSize (1, 80)
        self.SetColSize (2, 150)
        self.SetColSize (3, 150)
        self.SetColSize (4, 60)

        self.redraw ()
        self.Bind (wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelClick)

    def redraw (self):
        for i in range (self._numRows):
            T = self._taskList.getTask (i)
            self.SetRowLabelAlignment (i, wx.LEFT)
            self.SetRowLabelValue (i, T.getName ())

            self.SetCellValue (i, 0, T.getTypeName ())

            self.SetCellValue (i, 1, str (T.getNumber ()))
            self.SetCellValue (i, 2, str (T.getPercentage ()) + " %")
            self.SetCellValue (i, 3, str (T.getDuration ()))
            self.drawRow (i)

    def drawRow (self, row):
        T = self._taskList.getTask (row)
        if T.getSelected ():
            self.SetCellValue (row, 4, "Yes")
        else:
            self.SetCellValue (row, 4, "No")

        for i in range (self._numCols):
            if T.getSelected ():
                self.SetCellBackgroundColour (row, i, "#C0ffC0")
            else:
                self.SetCellBackgroundColour (row, i, "#ffC0C0")

    def EnableRow (self, row, enable):
        T = self._taskList.getTask (row)
        T.setSelected (enable)

        self.drawRow (row)
            
    def setReverseCols (self):
        for i in range (self._numCols):
            self._reverseCols= [False, False, False, False, False]

    def OnLabelClick (self, event):
        row = event.GetRow()
        col = event.GetCol()

        if row == -1:
            if col == -1:
                oldValue = self._reverseCols [0]
                self._taskList.sortByName (self._reverseCols[0])
                self.setReverseCols ()
                self._reverseCols [0] = not oldValue
            elif col == 0:
                oldValue = self._reverseCols [1]
                self._taskList.sortByType (self._reverseCols[1])
                self.setReverseCols ()
                self._reverseCols [1] = not oldValue
            elif col == 1:
                oldValue = self._reverseCols [3]
                self._taskList.sortByNumber (self._reverseCols[3])
                self.setReverseCols ()
                self._reverseCols [3] = not oldValue
            elif col == 2 or col == 3:
                oldValue = self._reverseCols [2]
                self._taskList.sortByExecutionTime (self._reverseCols[2])
                self.setReverseCols ()
                self._reverseCols [2] = not oldValue
            self.redraw ()
        else:
            # toggle row
            T = self._taskList.getTask (row)
            self.EnableRow (row, not T.getSelected ())

    def SelectAll (self):
        for i in range (self._taskList.getNumberOfTasks ()):
            self.EnableRow (i, True)


    def UnselectAll (self):
        print "UnselectAll"
        for i in range (self._taskList.getNumberOfTasks ()):
            self.EnableRow (i, False)

    def getTdiFile (self):
        return self._tdiFile

class ShowDialog (wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__ (self, parent, wx.ID_ANY, title)
        self.SetIcon (wx.Icon ('tdv.ico', wx.BITMAP_TYPE_ICO))

app = wx.App ()
TDGUI (None, -1, "Time Doctor GUI", sys.argv[1])
app.MainLoop ()
