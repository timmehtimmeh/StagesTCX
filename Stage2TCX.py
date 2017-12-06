#!/usr/bin/env python
#
# [SNIPPET_NAME: Calendar/Date picker]
# [SNIPPET_CATEGORIES: PyQt5]
# [SNIPPET_DESCRIPTION: A calendar/date picker example]
# [SNIPPET_AUTHOR: Darren Worrall <dw@darrenworrall.co.uk>]
# [SNIPPET_LICENSE: GPL]
# [SNIPPET_DOCS: http://www.riverbankcomputing.co.uk/static/Docs/PyQt5/html/qcalendarwidget.html]

# example calendar.py

from sys import *
from datetime import timedelta, date
from PyQt5.QtCore import QObject, pyqtSignal, QDir, QFileInfo, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QComboBox, QPushButton, QLabel, QGridLayout, QHBoxLayout,QVBoxLayout, QWidget, QApplication,QCalendarWidget,QAction, qApp,QTextEdit,QFileDialog,)
from tcx_writer import *
from subprocess import *
from plotCanvas import *


class Calendar(QMainWindow):
    """
    A QCalendarWidget example
    """

    def __init__(self):

        # create GUI
        QMainWindow.__init__(self)
        self.setWindowTitle('Calendar widget')
        # Set the window dimensions
        self.resize(800,600)
        self.setMinimumSize(700,500)

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open')
        openAction.triggered.connect(self.open_chooser)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        self.displayMenu = menubar.addMenu('&Display')
        pwrChecked = QAction('Power',self.displayMenu,checkable=True)
        cadChecked = QAction('Cadence',self.displayMenu,checkable=True)
        speedChecked = QAction('Speed',self.displayMenu,checkable=True)
        hrChecked = QAction('Heartrate',self.displayMenu,checkable=True)
        distanceChecked = QAction('Distance',self.displayMenu,checkable=True)

        self.displayMenu.addAction(pwrChecked)
        self.displayMenu.addAction(cadChecked)
        self.displayMenu.addAction(speedChecked)
        self.displayMenu.addAction(hrChecked)
        self.displayMenu.addAction(distanceChecked)

        pwrChecked.setChecked(True)
        cadChecked.setChecked(True)
        self.displayMenu.triggered.connect(self.updatePlot)

        # vertical layout for widgets
        vbox = QVBoxLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)

        #set the central widget as a gridbox
        topLayout = QHBoxLayout()
        topWidget = QWidget(self)
        topWidget.setLayout(topLayout)

        #widget to hold calendar and time selection
        calSelLayout = QVBoxLayout()
        calSelWidget = QWidget(self)
        calSelWidget.setLayout(calSelLayout)

        # Create a calendar widget and add it to our layout
        self.cal = QCalendarWidget()
        self.cal.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        #calSelLayout.setAlignment(self.cal,Qt.AlignTop)

        #and create a texteditor to show the read file
        # self.textEdit = QTextEdit()
        # gridbox.addWidget(self.textEdit,0,1)

        timeSelLayout = QHBoxLayout()
        timeSelWidget = QWidget(self)
        timeSelWidget.setLayout(timeSelLayout)

        # Create the hours combobox
        self.hoursBox = QComboBox()
        self.hoursBox.addItems(["12","1","2","3","4","5","6","7","8","9","10","11"])
        self.hoursBox.setCurrentIndex(4)
        self.hoursBox.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        timeSelLayout.addWidget(self.hoursBox)

        # Create the minutes combo box
        self.minutesBox = QComboBox()
        self.minutesBox.addItems(["00","15","30","45"])
        self.minutesBox.setCurrentIndex(3)
        self.minutesBox.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        timeSelLayout.addWidget(self.minutesBox)

        # Create the Am/Pm combo box
        self.ampmBox = QComboBox()
        self.ampmBox.addItems(["AM","PM"])
        self.ampmBox.setCurrentIndex(1)
        self.ampmBox.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        timeSelLayout.addWidget(self.ampmBox)



        # Create a label which we will use to show the date a week from now
        self.lbl = QLabel()
        timeSelLayout.addWidget(self.lbl)

        calSelLayout.addWidget(self.cal)
        calSelLayout.addWidget(timeSelWidget)
        calSelLayout.setAlignment(timeSelWidget,Qt.AlignTop)
        topLayout.addWidget(calSelWidget)

        bottomLayout = QHBoxLayout()
        bottomWidget = QWidget(self)
        bottomWidget.setLayout(bottomLayout)
        bottomLayout.setAlignment(Qt.AlignRight)

        # Create a process button
        self.goButton = QPushButton('Convert to TCX')
        self.goButton.setEnabled(False)
        self.goButton.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        bottomLayout.addWidget(self.goButton)
        self.goButton.clicked.connect(self.DoWork)

        self.plotter = PlotCanvas()
        self.plotter.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        topLayout.addWidget(self.plotter)

        vbox.addWidget(topWidget)
        vbox.addWidget(bottomWidget)

        # Connect the clicked signal to the centre handler
        self.cal.selectionChanged.connect(self.date_changed)
        #self.connect(self.cal, QtCore.SIGNAL('selectionChanged()'), self.date_changed)
        self.outName = ''
        self.fileName = ''
        self.hours = (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone)/3600
        self.minutes = 0
        self.date_changed()
        self.statusBar().showMessage('Please open csv file')
        self.show()

    def output_name(self,iname):
        # validate name ends with .CSV
        if iname.lower().endswith(".csv"):
            prefix = iname[:-3]
            oname = prefix + "tcx"
            if not os.path.exists(oname):
                return oname
            else:
                msgbox = QMessageBox()
                msgbox.setText("File %s exists, overwrite?" % oname)
                msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                retval = msgbox.exec_()
                if retval == QMessageBox.Yes:
                    os.remove(oname)
                    return oname
                else:
                    raise Exception('File %s already exists. Cannot continue.' % oname)
        else:
            raise Exception("%s does not end with .csv" % iname)

    def getCalendarTime(self):
        offset = (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone)/3600
        self.hours = int(self.hoursBox.currentText())+int(offset)
        if(self.ampmBox.currentText() == "PM"):
            self.hours += 12
        if (self.hours>=24):
            self.hours = self.hours-24
        self.minutes = int(self.minutesBox.currentText())
        print(self.pydate)
        print(self.hours)
        print(self.minutes)
        print(datetime.time(self.hours,self.minutes))
        dt = datetime.datetime.combine(self.pydate,datetime.time(self.hours,self.minutes))
        return dt

    def DoWork(self):

        if self.fileName:
            try:
                self.workout.setStartTime(self.getCalendarTime())
            except:
                print("Error setting start time")
                self.statusBar().showMessage('Error setting start time')
            try:
                self.outName = self.output_name(self.fileName)
            except:
                print("Error setting output name to " + self.outName )
                self.statusBar().showMessage('Error setting output name to '+ self.outName )
            try:
                tcx_writer(self.workout).writeTCX(self.outName)
                self.statusBar().showMessage('Success writing TCX: %s' % self.outName)
                Popen_arg = r'explorer /select, "' + self.outName.replace('/','\\') + '"'
                Popen(Popen_arg)
            except:
                print("Error creating file "+ self.outName)
                self.statusBar().showMessage('Error creating file ' + self.outName)

    def date_changed(self):
        """
        Handler called when the date selection has changed
        """
        # Fetch the currently selected date, this is a QDate object
        self.date = self.cal.selectedDate()
        # This is a gives us the date contained in the QDate as a native
        # python date[time] object
        self.pydate = self.date.toPyDate()
        # Calculate the date a week from now
        # sevendays = timedelta(days=7)
        # aweeklater = self.pydate + sevendays
        # Show this date in our label
        self.lbl.setText('The selected date is: %s' % self.pydate)

    def get_date(self):
        return self.date

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","CSV files (*.csv);;All Files (*)", options=options)
        if fileName:
            print(fileName)
        return fileName

    def open_chooser(self):
        self.fileName = self.openFileNameDialog()
        if self.fileName:
            self.workout = StagesWorkout(self.fileName,self.getCalendarTime())
            self.plotter.setWorkout(self.workout)
            self.goButton.setEnabled(True)
            self.statusBar().showMessage('Successfully read %i stages in %s' % (len(self.workout.stages), self.fileName))
            self.updatePlot()

    def updatePlot(self):
        actions = []
        for action in self.displayMenu.actions():
             if action.isChecked():
                 actions.append(action.text())
        print(actions)
        self.plotter.plot(actions)

# If the program is run directly or passed as an argument to the python
# interpreter then create a Calendar instance and show it
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = Calendar()
    app.exec_()
