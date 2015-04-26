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

import matplotlib
matplotlib.use ('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg, NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
import os
import wx
import Task

class Plotter (wx.Frame):

    # Colors for each core as RGBA tuple, max 8
    COLORS = [(0.5, 0.,0.,1.), (0., 0.5, 0.,1.), (0.,0.,0.5,1.), 
        (0.5,0.5,0.,1.), (0.5, 0., 0.5,1.), (0.,0.5, 0.5, 1.),
        (0.,0.,0.,1.), (0.5, 0.25, 0.25, 1.)]

    Y_INITIAL = 10
    Y_LABEL_INITIAL = 20
    Y_STEP = 20

    def __init__ (self, parent, taskList, separateThreads, iniTime, endTime):
        self._taskList = taskList
        self._separateThreads = separateThreads
        self._iniTime = iniTime
        self._endTime = endTime
        fileName = os.path.basename (self._taskList.getFileName ())
        wx.Frame.__init__ (self, parent, wx.ID_ANY, "Showing " + fileName)
        self.SetIcon (wx.Icon ('tdv.ico', wx.BITMAP_TYPE_ICO))
        matplotlib.rc ('ytick', labelsize=7)
        matplotlib.rc ('xtick', labelsize=7)

        self.fig = Figure((9,8), 75)
        self.canvas = FigureCanvasWxAgg (self, -1, self.fig)
        self.toolbar = NavigationToolbar2Wx(self.canvas)

        # On Windows, default frame size behaviour is incorrect
        # you don't need this under Linux
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))
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
                if self._separateThreads:
                    cores = T.getCoreList ()
                    for c in cores:
                        numRows += 1
                        label_y.append (yl)
                        yl += Plotter.Y_STEP
                        y += Plotter.Y_STEP
                        grid_y.append (y)
                        name = T.getName () + "_" + str(c)
                        y_names.append (name)
                else:
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
                xlim =(self._iniTime , self._endTime), ylim =(-10, 220))
        posY = Plotter.Y_INITIAL + 1

        segments = []
        colors = []

        for T in reversed (self._taskList._tasks):
            if T.getSelected ():
                if self._separateThreads:
                    coreList = T.getCoreList ()
                    for c in coreList:
                        for e in T._executions:
                            if c == e.getCore ():
                                if e.getTimeIn () > self._iniTime and \
                                    e.getTimeOut () < self._endTime:
                                    color = Plotter.COLORS [c]
                                    s = [[e.getTimeIn (), posY], 
                                        [e.getTimeIn (), posY + Plotter.Y_STEP -2],
                                        [e.getTimeOut (), posY + Plotter.Y_STEP -2],
                                        [e.getTimeOut (), posY]]
                                    segments.append (s)
                                    colors.append (color)
                        posY += Plotter.Y_STEP
                else:
                    for e in T._executions:
                        if e.getTimeIn () > self._iniTime and \
                            e.getTimeOut () < self._endTime:
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

        ax1.xaxis.set_major_formatter (plt.FuncFormatter (self.x_formatter))
        ax1.xaxis.set_ticks_position ('top')

        ax1.grid (True)

        self.toolbar.update ()

    def x_formatter (self, x, pos):
        return Task.TaskList.getTimeFormatted (x)

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

