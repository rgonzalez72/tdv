#!/usr/bin/python

import wx
from wx.lib import sheet

class TDGUI (wx.Frame):
    def __init__ (self, parent, id, title):
        wx.Frame.__init__ (self, parent, id, title, size= (800, 600))

        self.statusbas = self.CreateStatusBar ()
        self.CreateMenuBar ()

        self.graphics = TaskGrid (self)
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
    def __init__ (self, parent):
        sheet.CSheet.__init__ (self, parent)
        self.SetNumberRows (60)
        self.SetNumberCols (5)

        self.SetColLabelValue (0, "Type")
        self.SetColLabelValue (1, "Number")
        self.SetColLabelValue (2, "Percentage")
        self.SetColLabelValue (3, "Accumulated time")
        self.SetColLabelValue (4, "Show")

        self.SetColSize (0, 60)
        self.SetColSize (1, 80)
        self.SetColSize (2, 100)
        self.SetColSize (3, 200)
        self.SetColSize (4, 60)

        for i in range (60):
            self.SetCellValue (i, 4, "Yes")

        self.Bind (wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelClick)
            
    def OnLabelClick (self, event):
        row = event.GetRow()
        col = event.GetCol()

        if row == -1 and col == -1:
            pass
        if row == -1:
            pass
        else:
            # toggle row
            if self.GetCellValue (row, 4) == "Yes":
                self.SetCellValue (row, 4, "No")
            else:
                self.SetCellValue (row, 4, "Yes")

        event.Skip ()

app = wx.App ()
TDGUI (None, -1, "Time Doctor GUI")
app.MainLoop ()
