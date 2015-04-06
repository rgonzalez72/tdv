#!/usr/bin/python

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


import wx
import os
from wx.lib import sheet
import wx.lib.scrolledpanel as scrolled
import sys
import Task
import plotter

class TDGUI (wx.Frame):
    def __init__ (self, parent, id, title):
        wx.Frame.__init__ (self, parent, id, title, size= (800, 600))
        self.SetIcon (wx.Icon ('tdv.ico', wx.BITMAP_TYPE_ICO))

        self.statusbar = self.CreateStatusBar ()
        self.CreateMenuBar ()

        vbox = wx.BoxSizer (wx.VERTICAL)
        hbox0 = wx.BoxSizer (wx.HORIZONTAL)
        hbox1 = wx.BoxSizer (wx.HORIZONTAL)

        self.notebook = wx.Notebook (self, wx.ID_ANY, style= wx.RIGHT)

        self._sheets = []
        self._currentSheet = 0

        self.btnSel = wx.Button (self, wx.ID_ANY, "&Show")
        self.btnUnsel = wx.Button (self, wx.ID_ANY, "Hi&de") 
        self.btnSelAll = wx.Button (self, wx.ID_ANY, "Show &All")
        self.btnUnselAll = wx.Button (self, wx.ID_ANY, "H&ide All")
        self.btnShow = wx.Button (self, wx.ID_ANY, "&Visualize")
        
        # Disable the buttons until we load a file 
        self.btnSel.Disable ()
        self.btnUnsel.Disable ()
        self.btnSelAll.Disable ()
        self.btnUnselAll.Disable ()
        self.btnShow.Disable ()

        vbox.Add (self.notebook, 1, wx.EXPAND)

        hbox1.Add (self.btnSel, 0, wx.CENTER | wx.RIGHT, 20)
        hbox1.Add (self.btnUnsel, 0, wx.CENTER | wx.RIGHT, 20)
        hbox1.Add (self.btnSelAll, 0, wx.CENTER | wx.RIGHT, 20)
        hbox1.Add (self.btnUnselAll, 0, wx.CENTER, 20)
        hbox1.Add (self.btnShow, 0, wx.CENTER | wx.LEFT, 20)
        
        vbox.Add ((5,5) , 0)
        vbox.Add (hbox1, 0, wx.CENTER)
        self.SetSizer(vbox)

        self.Bind (wx.EVT_BUTTON, self.OnSelect, self.btnSel)
        self.Bind (wx.EVT_BUTTON, self.OnUnselect, self.btnUnsel)
        self.Bind (wx.EVT_BUTTON, self.OnSelectAll, self.btnSelAll)
        self.Bind (wx.EVT_BUTTON, self.OnUnselectAll, self.btnUnselAll)
        self.Bind (wx.EVT_BUTTON, self.OnShow, self.btnShow)
        self.Bind (wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnChange, self.notebook)

        
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
        diag = wx.FileDialog (self, "Select a time doctor file to open", 
                os.getcwd(), "", "Time doctor files (*.tdi)|*.tdi|" +
                "All files|*.*", wx.OPEN)

        if diag.ShowModal () == wx.ID_OK:
            tdiFileName =  diag.GetFilename ()
            self.dlg = wx.ProgressDialog ("Recover information",\
                "Loading time doctor file: " + tdiFileName, 100, self)
            self.dlg.Update (10)
            fullPath = os.path.join (diag.GetDirectory(), tdiFileName)
            taskList = Task.TaskList ()
            self.dlg.Update (20)
            taskList.readTDFile (fullPath)
            self.dlg.Update (40)
            taskList.calcPercentage ()
            self.dlg.Update (60)
            taskList.sortByName ()
            self.dlg.Update (80)
            self.dlg.Destroy ()
            sheet = TaskGrid (self.notebook, tdiFileName, taskList, self)
            sheet.SetFocus ()
            self._sheets.append (sheet)
            self.notebook.AddPage (sheet, tdiFileName, True)
            self.btnSelAll.Enable ()
            self.btnUnselAll.Enable ()
            self.btnShow.Enable ()

    def OnCloseFile (self, e):
        if len(self._sheets) == 0:
            return 
        sel = self.notebook.GetSelection ()
        newSheets = []
        if sel > 0:
            newSheets = self._sheets [:sel]
        elif sel < len (self._sheets) -1:
            newSheets = self._sheets [sel+1:]
        self._sheets = newSheets
        self.notebook.RemovePage (sel)
        if len (self._sheets) == 0:
            self.btnSel.Disable ()
            self.btnUnsel.Disable ()
            self.btnSelAll.Disable ()
            self.btnUnselAll.Disable ()
            self.btnShow.Disable ()
            self.statusbar.SetStatusText (' ')

    def OnSelect (self, e):
        self._sheets [self._currentSheet].SelectRange ()
        if self._sheets [self._currentSheet]._taskList.isAnyTaskSelected ():
            self.btnShow.Enable ()

    def OnUnselect (self, e):
        self._sheets [self._currentSheet].UnselectRange ()
        if not self._sheets [self._currentSheet]._taskList.isAnyTaskSelected ():
            self.btnShow.Disable ()

    def OnSelectAll (self, e):
        self._sheets [self._currentSheet].SelectAll ()
        if self._sheets [self._currentSheet]._taskList.isAnyTaskSelected ():
            self.btnShow.Enable ()

    def OnUnselectAll (self, e):
        self._sheets [self._currentSheet].UnselectAll ()
        if not self._sheets [self._currentSheet]._taskList.isAnyTaskSelected ():
            self.btnShow.Disable ()

    def OnShow (self, e):
        frame = plotter.Plotter (self, self._sheets [self._currentSheet].getClonedList ())
        frame.Show ()

    def OnChange (self, e):
        self._currentSheet = e.GetSelection ()
        S = self._sheets [ self._currentSheet].getList ()
        statusText = "Total time: " + S.getTimeFormatted (S.getLastTime ()) + \
            ", Number of cores: " + str(S.getNumberOfCores ()) + \
            ", Number of threads: " + str (S.getNumberOfTasks ())
        self.statusbar.SetStatusText (statusText)

    def EnableSelect (self):
        self.btnSel.Enable ()
        self.btnUnsel.Enable ()

    def DisableSelect (self):
        self.btnSel.Disable ()
        self.btnUnsel.Disable ()

class AboutDialog (wx.Dialog):
    def __init__ (self, parent, id, title):
        wx.Dialog.__init__ (self, parent, id, title)

        vbox = wx.BoxSizer (wx.VERTICAL)
        hbox0 = wx.BoxSizer (wx.HORIZONTAL)
        hbox1 = wx.BoxSizer (wx.HORIZONTAL)
        hbox2 = wx.BoxSizer (wx.HORIZONTAL)
        hbox3 = wx.BoxSizer (wx.HORIZONTAL)

        panel = wx.Panel (self, wx.ID_ANY)
    
        picturePanel = wx.Panel (panel, wx.ID_ANY)
        picture = wx.StaticBitmap (picturePanel)
        im = wx.Image ('tdv.png')
        picture.SetBitmap (wx.BitmapFromImage (im))
        hbox0.Add (picturePanel, 0, wx.LEFT | wx.RIGHT, 20 )



        label1 = wx.StaticText (panel, wx.ID_ANY, 
                "An application for visualizing time doctor files.")
        hbox1.Add (label1, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)

        VERSION = "eng.0.0.1"
        label1 = wx.StaticText (panel, wx.ID_ANY, "Version: " + VERSION)
        hbox2.Add (label1, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)

        self.btnClose = wx.Button (panel, wx.ID_CLOSE, "&Close")
        hbox3.Add (self.btnClose, 0, wx.CENTER, 20)
        self.Bind (wx.EVT_BUTTON, self.OnClose, self.btnClose)

        vbox.Add (hbox0, 0, wx.CENTER)
        vbox.Add (hbox1, 0, wx.LEFT)
        vbox.Add (hbox2, 0, wx.CENTER)
        vbox.Add (hbox3, 0, wx.CENTER)

        panel.SetSizer(vbox)
        minSize = vbox.GetMinSize()
#  height = minSize.GetHeight ()
#        minSize.SetHeight (height + 60)
        self.SetSize (minSize )


    def OnClose (self, e):
        self.Close ()

class TaskGrid (sheet.CSheet):
    def __init__ (self, parent, tdiFile, taskList, mainWin):
        sheet.CSheet.__init__ (self, parent)
        self._mainWin = mainWin

        self._taskList = taskList
        self._tdiFile = tdiFile

        self._numRows = self._taskList.getNumberOfTasks ()
        self._numCols = 6
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
        self.SetColLabelValue (4, "Cores")
        self.SetColLabelValue (5, "Show")

        self.SetRowLabelSize (150)
        self.SetColSize (0, 60)
        self.SetColSize (1, 80)
        self.SetColSize (2, 150)
        self.SetColSize (3, 150)
        self.SetColSize (4, 60)

        self._selected = []

        self.Bind (wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelClick)
        self.Bind (wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.redraw ()

    def redraw (self):
        for i in range (self._numRows):
            T = self._taskList.getTask (i)
            self.SetRowLabelAlignment (i, wx.LEFT)
            self.SetRowLabelValue (i, T.getName ())

            self.SetCellValue (i, 0, T.getTypeName ())

            self.SetCellValue (i, 1, str (T.getNumber ()))
            self.SetCellValue (i, 2, str (T.getPercentage ()) + " %")
            self.SetCellValue (i, 3, str (T.getTotalDuration ()))
            self.SetCellValue (i, 4, T.getCoreString ())
            self.drawRow (i)

    def drawRow (self, row):
        T = self._taskList.getTask (row)
        if T.getSelected ():
            self.SetCellValue (row, 5, "Yes")
        else:
            self.SetCellValue (row, 5, "No")

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
            elif col == 4:
                oldValue = self._reverseCols [4]
                self._taskList.sortByCores (self._reverseCols[4])
                self.setReverseCols ()
                self._reverseCols [4] = not oldValue
            self.redraw ()
        else:
            # toggle row
#T = self._taskList.getTask (row)
#            self.EnableRow (row, not T.getSelected ())
            event.Skip ()

    def OnRangeSelect (self, e):
        if e.Selecting () == False:
            self._selected = []
            self._mainWin.DisableSelect ()
        else:
            for i in range (e.GetTopRow (), e.GetBottomRow () + 1):
                self._selected.append (i)
            self._mainWin.EnableSelect ()

    def SelectRange (self):
        for row in self._selected:
            T = self._taskList.getTask (row)
            self.EnableRow (row, True)

    def UnselectRange (self):
        for row in self._selected:
            T = self._taskList.getTask (row)
            self.EnableRow (row, False)

    def SelectAll (self):
        for i in range (self._taskList.getNumberOfTasks ()):
            self.EnableRow (i, True)


    def UnselectAll (self):
        for i in range (self._taskList.getNumberOfTasks ()):
            self.EnableRow (i, False)

    def getTdiFile (self):
        return self._tdiFile

    def getClonedList (self):
        return self._taskList.clone ()

    def getList (self):
        return self._taskList



app = wx.App ()
TDGUI (None, -1, "Time Doctor Visualizer")
app.MainLoop ()
