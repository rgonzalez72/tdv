#!/usr/bin/python

import matplotlib
matplotlib.use ('WX')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_wx import Toolbar, FigureCanvasWx, FigureManager
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
import os
import wx

class Plotter (wx.Frame):

    # Colors for each core as RGBA tuple, max 8
    COLORS = [(0.5, 0.,0.,1.), (0., 0.5, 0.,1.), (0.,0.,0.5,1.), 
        (0.5,0.5,0.,1.), (0.5, 0., 0.5,1.), (0.,0.5, 0.5, 1.),
        (0.,0.,0.,1.), (0.5, 0.25, 0.25, 1.)]

    Y_INITIAL = 10
    Y_LABEL_INITIAL = 20
    Y_STEP = 20
    
    def __init__ (self, parent, taskList):
        self._taskList = taskList
        fileName = os.path.basename (self._taskList.getFileName ())
        wx.Frame.__init__ (self, parent, wx.ID_ANY, "Showing " + fileName)
        self.SetIcon (wx.Icon ('tdv.ico', wx.BITMAP_TYPE_ICO))

        self.fig = Figure((9,8), 75)
        self.canvas = FigureCanvasWx (self, -1, self.fig)
        self.toolbar = Toolbar(self.canvas)

        # On Windows, default frame size behaviour is incorrect
        # you don't need this under Linux
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))
        # Create a figure manager to manage things
        self.figmgr = FigureManager(self.canvas, 1, self)
        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

        # Calculate the number of rows
        numRows = 0
        # Label position
        label_y = []
        yl = Plotter.Y_LABEL_INITIAL
        y = Plotter.Y_INITIAL
        grid_y = [y]
        y_names = []
        for T in reversed (self._taskList._tasks):
            if T.getSelected ():
                numRows += 1
                label_y.append (yl)
                yl += Plotter.Y_STEP
                y += Plotter.Y_STEP
                grid_y.append (y)
                y_names.append (T.getName ())


        majl = plt.FixedLocator (grid_y)
        minl = plt.FixedLocator (label_y)
        minf = y_names

        fileName = os.path.basename (self._taskList.getFileName ())

        ax1 = self.fig.add_subplot (111, autoscale_on=False,  
                xlim =(0,self._taskList.getLastTime()), ylim =(0, 220))
        posY = Plotter.Y_INITIAL + 1

        segments = []
        colors = []

        for T in reversed (self._taskList._tasks):
            if T.getSelected ():
                for e in T._executions:
                    color = Plotter.COLORS [e.getCore ()]
                    s = [[e.getTimeIn (), posY], 
                         [e.getTimeIn (), posY + Plotter.Y_STEP -2],
                         [e.getTimeOut (), posY + Plotter.Y_STEP -2],
                         [e.getTimeOut (), posY]]
                    segments.append (s)
                    colors.append (color)
                posY += Plotter.Y_STEP

        coll = LineCollection (segments, lw=2, colors=colors)
        ax1.add_collection (coll)

        ax1.yaxis.set_major_locator (majl)
        ax1.yaxis.set_minor_locator (minl)
        ax1.yaxis.set_major_formatter (plt.FormatStrFormatter (''))
        ax1.yaxis.set_minor_formatter (plt.FixedFormatter(minf))

        ax1.grid (True)

        self.toolbar.update ()

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

