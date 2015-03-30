#!/usr/bin/python

import wx

class TDGUI (wx.Frame):
    def __init__ (self, parent, id, title):
        wx.Frame.__init__ (self, parent, id, title, size= (800, 600))

        self.statusbas = self.CreateStatusBar ()
        self.CreateMenuBar ()
        
        self.Centre ()
        self.Show (True)

    def CreateMenuBar (self):
        menubar = wx.MenuBar ()
        filem = wx.Menu ()
        helpm = wx.Menu ()

        Qitem = filem.Append (wx.ID_EXIT, "&Quit", "Quit application")
        menubar.Append (filem, "&File")
        menubar.Append (helpm, "&Help")

        self.SetMenuBar (menubar)

        self.Bind (wx.EVT_MENU, self.OnQuit, Qitem)

    def OnQuit (self, e):
        self.Close ()

app = wx.App ()
TDGUI (None, -1, "Time Doctor GUI")
app.MainLoop ()
