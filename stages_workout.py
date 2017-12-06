import re
import os
import sys
import time
import getopt
import datetime



def convertToSeconds(timeString):
    ret = 0
    times = timeString.split(':')

    #times = map(int, re.split(r"[:,.]", timeString))
    try:
        if(len(times)>3):
            ret = int(times[0])*3600+int(times[1])*60+times[2]+int(times[3])/1000
        elif(len(times)>2):
            ret = int(times[0])*3600+int(times[1])*60+int(times[2])
        elif(len(times)>1):
            ret=int(times[0])*60+int(times[1])
        else:
            ret=int(times[0])
    except ValueError:
        print("Error parsing number of seconds")
    return ret

class WorkoutPoint:
    def __init__(self,csvrow):
        splitrow=csvrow.split(',')
        self.Time = convertToSeconds(splitrow[0])
        self.Distance = float(splitrow[1])
        self.Speed = float(splitrow[2])
        self.Power = int(splitrow[3])
        self.HR = int(splitrow[4])
        self.RPM = int(splitrow[5])


class WorkoutStage:
    def __init__(self):
        self.stageNum = -1
        self.stageTime = 0
        self.stageDist = 0.0
        self.stageAvgSpeed = 0.0
        self.stageAvgPower = 0
        self.stageAvgHR = 0
        self.stageAvgCadence = 0
        self.stageMaxSpeed = 0.0
        self.stageMaxPower = 0
        self.stageMaxHR = 0
        self.stageMaxCadence = 0
        self.stageKCAL = 0
        self.stageKJ = 0
        self.workoutPoints = []

    def fixDistances(self):
        numPts = len(self.workoutPoints)
        totalDistance =0.0
        for i in range(numPts):
            #
            # deltaDistance = self.workoutPoints[i].Distance - self.workoutPoints[0].Distance
            # totalDistance +=  deltaDistance / 3600
            # currStageTime = self.workoutPoints[i].Time - self.workoutPoints[0].Time
            # self.workoutPoints[i].Distance = totalDistance / currStageTime
            if i>0:
                totalDistance += self.workoutPoints[i].Speed / 3600
            self.workoutPoints[i].Distance = totalDistance + self.workoutPoints[0].Distance


    def ReadStage(self,fil):
        line = fil.readline()
        while True:
            self.workoutPoints.append(WorkoutPoint(line))
            line = fil.readline()
            if("Stage" in line or "Ride_Totals" in line):
                self.fixDistances();
                break
        if "Stage" in line:
            self.stageNum = int(re.search(r'\d+', line).group()) # Stage_01
            self.ReadStageStats(fil)
            print ("Successfully read stage ", self.stageNum)
            return 0
        if "Ride_Totals" in line:
            #the last "stage" doesn't have stage statistics, so calculate them
            self.CalculateStageStats()
            return 1

    def CalculateStageStats(self):
        numPts = len(self.workoutPoints)
        self.stageTime = self.workoutPoints[numPts-1].Time - self.workoutPoints[0].Time
        self.stageDist = self.workoutPoints[numPts-1].Distance - self.workoutPoints[0].Distance

        stageAvgSpeed = 0.0
        stageAvgPower = 0
        stageAvgHR = 0
        stageAvgCadence = 0

        for i in range(numPts):
            stageAvgSpeed += self.workoutPoints[i].Speed / numPts
            stageAvgPower += self.workoutPoints[i].Power / numPts
            stageAvgHR += self.workoutPoints[i].HR / numPts
            stageAvgCadence += self.workoutPoints[i].RPM / numPts
            if (self.workoutPoints[i].Speed > self.stageMaxSpeed):
                self.stageMaxSpeed = self.workoutPoints[i].Speed
            if(self.workoutPoints[i].Power > self.stageMaxPower ):
                self.stageMaxPower = self.workoutPoints[i].Power
            if(self.workoutPoints[i].HR > self.stageMaxHR ):
                self.stageMaxHR = self.workoutPoints[i].HR
            if(self.workoutPoints[i].RPM > self.stageMaxCadence ):
                self.stageMaxCadence = self.workoutPoints[i].RPM

        self.stageAvgSpeed = stageAvgSpeed
        self.stageAvgPower = int(stageAvgPower)
        self.stageAvgHR = int(stageAvgHR)
        self.stageAvgCadence = int(stageAvgCadence)


    def ReadStageStats(self,fil):
        self.stageTime = convertToSeconds(fil.readline().split(',')[1])
        self.stageDist = float(fil.readline().split(',')[1])
        self.stageAvgSpeed = float(fil.readline().split(',')[1])
        self.stageAvgPower = int(fil.readline().split(',')[1])
        self.stageAvgHR = int(fil.readline().split(',')[1])
        self.stageAvgCadence = int(fil.readline().split(',')[1])
        self.stageMaxSpeed = float(fil.readline().split(',')[1])
        self.stageMaxPower = int(fil.readline().split(',')[1])
        self.stageMaxHR = int(fil.readline().split(',')[1])
        self.stageMaxCadence = int(fil.readline().split(',')[1])
        self.stageKCAL = int(fil.readline().split(',')[1])
        self.stageKJ = int(fil.readline().split(',')[1])

class StagesWorkout:
    def __init__(self,fileName,startTime):
        self.make = "Stages"
        self.model = "S3 Indoor bike"
        self.hw = 5
        self.totalTime = 0
        self.totalDist = 0.0
        self.maxSpeed = 0.0
        self.maxHR = 0
        self.maxCadence = 0
        self.maxPower = 0
        self.avgSpeed = 0.0
        self.avgHeart = 0
        self.avgCadence = 0
        self.avgPower = 0
        self.ttlDist = 0
        self.stages = []
        self.readCSV(fileName)
        self.setStartTime(startTime)
        #print (self.startsec)

    def setStartTime(self,startTime):
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = startTime - epoch
        self.startsec = delta.total_seconds()

    def ReadTotalStats(self,fil):
        self.totalTime = convertToSeconds(fil.readline().split(',')[1])
        self.totalDist = float(fil.readline().split(',')[1])
        self.avgSpeed = float(fil.readline().split(',')[1])
        self.avgPower = int(fil.readline().split(',')[1])
        self.avgHR = int(fil.readline().split(',')[1])
        self.avgCadence = int(fil.readline().split(',')[1])
        self.maxSpeed = float(fil.readline().split(',')[1])
        self.maxPower = int(fil.readline().split(',')[1])
        self.maxHR = int(fil.readline().split(',')[1])
        self.maxCadence = int(fil.readline().split(',')[1])
        self.stageKCAL = int(fil.readline().split(',')[1])
        self.stageKJ = int(fil.readline().split(',')[1])

    def readCSV(self,fileName):
        fp = open(fileName, 'rt')

        fp.readline()  # read Stages_Data
        fp.readline()  # read English
        self.validatePointHdr(fp.readline())  # read Time,Miles,MPH,Watts,HR,RPM
        try:
            ret = 0
            while ret == 0:
                currStage = WorkoutStage()
                ret = currStage.ReadStage(fp);
                self.stages.append(currStage)
            self.ReadTotalStats(fp)
            fp.close()
            print("Done reading all stages")

        except Exception as e:
            print(e)
            print(type(e))


    def validatePointHdr(self,csvrow):
        """
        We assume the order of the fields when parsing the points
        so we fail if the headers are unexpectedly ordered or
        missing or more than expected.
        """
        hdrs = csvrow.rstrip().split(',')
        if len(hdrs) != 6:
            raise Exception("Expected 6 cols, got %d" , len(csvrow))
        exp = []
        exp.append("Time")
        exp.append("Miles")
        exp.append("MPH")
        exp.append("Watts")
        exp.append("HR")
        exp.append("RPM")
        if exp != hdrs:
            raise Exception("Unexpected Header ",exp," != ",  hdrs)

    def printWorkout(self):
        print ("There are ", len(self.stages), " Stages in the workout")
        i = 0
        for stage in self.stages:
            i+=1
            print("Stage ",i," has ", len(stage.workoutPoints), " data points in it")

#test code
# if __name__ == "__main__":
#     StagesWorkout("STAGES04.csv",datetime.datetime.now()).printWorkout()
