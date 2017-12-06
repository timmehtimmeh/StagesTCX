from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QSizePolicy
from stages_workout import *

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.workoutSet = False
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def setWorkout(self,workout):
        self.workout = workout
        self.workoutSet = True

    def plot(self, plotItems):

        # if we haven't loaded a workout
        if not self.workoutSet:
            return

        self.figure.clear()
        self.figure.clf()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        ax = self.figure.add_subplot(111)

        ax.cla()

        # if we're not plotting anything
        if len(plotItems) == 0:
            return

        hndls = []
        power = []
        rpm = []
        hr = []
        speed = []
        distance = []

        numpts = 0
        for l in self.workout.stages:
            for p in l.workoutPoints:
                #print(p)
                power.append(p.Power)
                rpm.append(p.RPM)
                hr.append(p.HR)
                speed.append(p.Speed)
                distance.append(p.Distance)
                numpts +=1

        #set the x axis limit
        ax.set_xlim(0,numpts)

        dispPower = False
        dispSpeed = False
        dispCad = False
        dispHR  = False
        dispDist  = False
        ax2 = ax.twinx()
        for item in plotItems:
            if item == 'Power':
                dispPower = True
                pwr,=ax.plot(power, 'b-', label='Power (Watts)')
                hndls.append(pwr)
            if item == 'Speed':
                dispSpeed = True
                spd,=ax2.plot(speed, 'g-', label='Speed (Mph)')
                hndls.append(spd)
            if item == 'Cadence':
                dispCad = True
                cad,=ax.plot(rpm, 'k-', label='Cadence (Rpm)')
                hndls.append(cad)
            if item == 'Heartrate':
                dispHR = True
                hr,=ax.plot(hr, 'r-', label='Heartrate (Bpm)')
                hndls.append(hr)
            if item == 'Distance':
                dispDist = True
                dist,=ax2.plot(distance, '-', label='Distance (miles)')
                hndls.append(dist)

        #enable the legend
        ax.legend(handles=hndls)
        ax.set_title('Workout Data vs Time')
        ax.set_xlabel("Time (sec)")
        if dispPower or dispCad or dispHR:
            axlim = 0
            maxax = 0
            axlbl = ""
            if dispPower:
                maxax= max(maxax,self.workout.maxPower)
                axlbl = "Power (Watts)"

            if  dispCad:
                maxax= max(maxax,self.workout.maxCadence)
                if axlbl != "":
                    axlbl+=", Cadence (RPM)"
                else:
                    axlbl = "Cadence (RPM)"
            if dispHR:
                maxax= max(maxax,self.workout.maxHR)
                if axlbl != "":
                    axlbl+=", Heartrate (BPM)"
                else:
                    axlbl = "Heartrate (BPM)"

            ax.set_ylim(0,maxax)
            ax.set_ylabel(axlbl)


        if dispDist or dispSpeed:
            ax2lim = 0
            if dispDist and dispSpeed:
                ax2lbl ="Speed (mph),Distance (miles)"
                ax2lim = max(self.workout.totalDist,self.workout.maxSpeed)
            elif dispDist:
                ax2lbl ="Distance (miles)"
                ax2lim = self.workout.totalDist
            else:
                ax2lbl ="Speed (mph)"
                ax2lim = self.workout.maxSpeed
            ax2.set_ylim(0, ax2lim)
            ax2.set_ylabel(ax2lbl)
            ax2.set_xlim(0,numpts)
        self.draw()
