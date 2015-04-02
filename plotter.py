#!/usr/bin/python

from threading import Thread
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import os

class Plotter (Thread):

    # Colors for each core as RGBA tuple, max 8
    COLORS = [(0.5, 0.,0.,1.), (0., 0.5, 0.,1.), (0.,0.,0.5,1.), 
        (0.5,0.5,0.,1.), (0.5, 0., 0.5,1.), (0.,0.5, 0.5, 1.),
        (0.,0.,0.,1.), (0.5, 0.25, 0.25, 1.)]

    Y_INITIAL = 10
    Y_LABEL_INITIAL = 20
    Y_STEP = 20
    
    def __init__ (self, taskList):
        Thread.__init__ (self)
        self._taskList = taskList
        self.start ()

    def run (self):
        """Run the thread """
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

        fig = plt.figure (fileName)
        ax1 = fig.add_subplot (111, autoscale_on=False,  
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

        plt.show ()
