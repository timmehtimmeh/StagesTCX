from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from stages_workout import *

XSI = 'http://www.w3.org/2001/XMLSchema-instance'
XSD = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd'
XML_NS = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
EXT_NS = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'

class tcx_writer:
    def __init__(self, workout):
        self.workout = workout

    def isoTimestamp(self,seconds):
        # Use UTC for isoTimestamp
        tm = time.gmtime(seconds)
        return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", tm)

	#converts miles per hour to meters per second
    @staticmethod
    def metersPerSec(speed):
        return speed * 0.44704

    def writeTCX(self, file):
        tcdb = self.trainingCenterDB()
        et = ElementTree.ElementTree(tcdb)
        try:
            et.write(file, 'UTF-8', True)
        except TypeError:
            # pre-python 2.7
            et.write(file, 'UTF-8')

    def trainingCenterDB(self):
        dict = {'xsi:schemaLocation': XML_NS + ' ' + XSD,
                'xmlns': XML_NS,
                'xmlns:xsi': XSI}
        tcdb = Element('TrainingCenterDatabase', dict)
        acts = SubElement(tcdb, 'Activities')
        self.addActivity(acts)
        self.addAuthor(tcdb)
        return tcdb

    def addActivity(self, acts):
        act = SubElement(acts, 'Activity', {'Sport': 'Biking'})
        id = SubElement(act, 'Id')
        id.text = self.isoTimestamp(self.workout.startsec)
        count = 0
        for l in self.workout.stages:
            self.addLap(act,count)
            count = count +1
        #self.addCreator(act)

    def addCreator(self, act):
        c = SubElement(act, 'Creator', {'xsi:type': 'Device_t'})
        name = SubElement(c, 'Name')
        name.text = "%s %s" % (self.make, self.model)
        unit = SubElement(c, 'UnitId')
        unit.text = '0'
        prd = SubElement(c, 'ProductID')
        prd.text = str(self.hw)

    def addAuthor(self, tcdb):
        a = SubElement(tcdb, 'Author', {'xsi:type': 'Application_t'})
        name = SubElement(a, 'Name')
        name.text = 'Stages CSV to TCX Convertor'
        build = SubElement(a, 'Build')
        ver = SubElement(build, 'Version')
        vmaj = SubElement(ver, 'VersionMajor')
        vmaj.text = '1'
        vmin = SubElement(ver, 'VersionMinor')
        vmin.text = '0'
        bmaj = SubElement(ver, 'BuildMajor')
        bmaj.text = '0'
        bmin = SubElement(ver, 'BuildMinor')
        bmin.text = '0'
        lang = SubElement(a, 'LangID')
        lang.text = 'en'
        partnum = SubElement(a, 'PartNumber')
        partnum.text = '006-A0161-00'

    def addLap(self, act, lapNumber):
        st = self.isoTimestamp(self.workout.startsec + self.workout.stages[lapNumber].workoutPoints[0].Time)
        lap = SubElement(act, 'Lap', {'StartTime': st})
        last = len(self.workout.stages[lapNumber].workoutPoints) - 1
        tts = SubElement(lap, 'TotalTimeSeconds')
        tts.text = str(self.workout.stages[lapNumber].stageTime)
        dist = SubElement(lap, 'DistanceMeters')
        dist.text = str(self.workout.stages[lapNumber].stageDist*1609.34)
        ms = SubElement(lap, 'MaximumSpeed')
        #ms.text = str(Revolution.metersPerSec(self.maxSpeed))
        ms.text = str(self.workout.stages[lapNumber].stageMaxSpeed)
        calories = SubElement(lap, 'Calories')
        calories.text = str(self.workout.stages[lapNumber].stageKCAL)
        if self.workout.stages[lapNumber].stageAvgHR > 0:
            avgheart = SubElement(lap, 'AverageHeartRateBpm')
            avgheartvalue = SubElement(avgheart, 'Value')
            avgheartvalue.text = str(self.workout.stages[lapNumber].stageAvgHR)
        if self.workout.stages[lapNumber].stageMaxHR >0 :
            maxheart = SubElement(lap, 'MaximumHeartRateBpm')
            maxheartvalue = SubElement(maxheart, 'Value')
            maxheartvalue.text = str(self.workout.stages[lapNumber].stageMaxHR)
        intensity = SubElement(lap, 'Intensity')
        intensity.text = 'Active'
        cadence = SubElement(lap, 'Cadence')
        cadence.text = str(self.workout.stages[lapNumber].stageAvgCadence)
        trigger = SubElement(lap, 'TriggerMethod')
        trigger.text = 'Manual'
        lap.append(self.trackElement(lapNumber))
        ext = SubElement(lap, 'Extensions')
        self.LapExtension(ext, 'MaxBikeCadence', self.workout.stages[lapNumber].stageMaxCadence)
        avgspeed = self.workout.stages[lapNumber].stageAvgSpeed
		#avgspeed = self.ttlSpeed / (last+1)
        #avgspeed = Revolution.metersPerSec(self.ttlSpeed / (last+1))
        self.LapExtension(ext, 'AvgSpeed', avgspeed)
        avgwatts = self.workout.stages[lapNumber].stageAvgPower #self.ttlWatts / (last+1)
        self.LapExtension(ext, 'AvgWatts', avgwatts)
        self.LapExtension(ext, 'MaxWatts', self.workout.stages[lapNumber].stageMaxPower)

    def LapExtension(self, ext, tag, text):
        tpx = SubElement(ext, 'LX', {'xmlns': EXT_NS})
        value = SubElement(tpx, tag)
        value.text = str(text)

    def trackElement(self,lapNumber):
        t = Element('Track')
        for p in self.workout.stages[lapNumber].workoutPoints:
            t.append(self.trackpointElement(p, self.workout.startsec))
        return t

    def trackpointElement(self, workoutPoint, start):
        tp = Element('Trackpoint')
        time = SubElement(tp, 'Time')
        time.text = self.isoTimestamp(start + workoutPoint.Time)
        dist = SubElement(tp, 'DistanceMeters')
        dist.text = str(workoutPoint.Distance*1609.34)
        if workoutPoint.HR >0:
            heart = SubElement(tp, 'HeartRateBpm')
            heartvalue = SubElement(heart, 'Value')
            heartvalue.text = str(workoutPoint.HR)
        cadence = SubElement(tp, 'Cadence')
        cadence.text = str(workoutPoint.RPM)
        ext = SubElement(tp, 'Extensions')
        tpx = SubElement(ext, 'TPX', {'xmlns': EXT_NS})
        mph = workoutPoint.Speed;
        #mps = Revolution.metersPerSec(self.speed)
        speed = SubElement(tpx, 'MPH')
        speed.text = str(mph)
        watts = SubElement(tpx, 'Watts')
        watts.text = str(workoutPoint.Power)
        return tp

    def trackpointExtension(self, ext, tag, text):
        tpx = SubElement(ext, 'TPX', {'xmlns': EXT_NS})
        value = SubElement(tpx, tag)
        value.text = str(text)

# if __name__ == "__main__":
#     workout = StagesWorkout("STAGES04.csv",datetime.datetime.now())
#     tcx_writer(workout).writeTCX("Stage04.tcx")
