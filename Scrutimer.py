# Analog clock based on example: 
# https://doc.qt.io/qt-6/qtqml-syntax-basics.html
import sys
import datetime

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from time import strftime, localtime
from ScrutimerAnnouncement import ScrutimerAnnouncement

#FILE_NAME = "Data/FSG_All_Inspection_Time_Slots_short.csv" # FSG 2024
FILE_NAME = "Data/FSG25.csv" # FSG 2025
#FILE_NAME = "Scrutimer.tbl"
FILE_SEPARATOR = ";"
FILE_DATE_SEPARATOR = "-"
FILE_TIME_SEPARATOR = ":"

app = QGuiApplication(sys.argv)

engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)
engine.load('Scrutimer.qml')


class Backend(QObject):

    updated = pyqtSignal(str, arguments=['time'])
    hms = pyqtSignal(int, int, int, arguments=['hours','minutes','seconds'])
    accumulator_text = pyqtSignal(str, arguments=['slot_a'])
    electrical_text = pyqtSignal(str, arguments=['slot_e'])
    mechanical_text = pyqtSignal(str, arguments=['slot_m'])

    def __init__(self):
        super().__init__()

        # Define timer.
        self.timer = QTimer()
        self.timer.setInterval(100)  # msecs 100 = 1/10th sec
        self.timer.timeout.connect(self.update_time)
        self.timer.start()
        

    def update_time(self):
        # Pass the current time to QML.
        local_time = localtime()
        curr_time = strftime("%H:%M:%S", localtime())
        self.updated.emit(curr_time)
        self.hms.emit(local_time.tm_hour, local_time.tm_min, local_time.tm_sec)
        self.accumulator_text.emit(fsg_timetable.current_slot(category = "A"))
        self.electrical_text.emit(fsg_timetable.current_slot(category = "E"))
        self.mechanical_text.emit(fsg_timetable.current_slot(category = "M"))

class Slot():
    category = ""
    start = ""
    stop = ""
    comment = ""
    announce_5_min = False
    announce_over = False
    
    def __init__(self, datastr):
        splitstr = str(datastr).split(FILE_SEPARATOR)
        if len(splitstr) >= 3:
            splitstr[0] = splitstr[0].strip(" ")
            if splitstr[0][0] in "Aa":
                self.category = "A"
            elif splitstr[0][0] in "Ee":
                self.category = "E"
            elif splitstr[0][0] in "Mm":
                self.category = "M"
            elif splitstr[0][0] in "Ll":
                if splitstr[4][0] in "Aa":
                    self.category = "LA"
                elif splitstr[4][0] in "Ee":
                    self.category = "LE"
                elif splitstr[4][0] in "Mm":
                    self.category = "LM"
                else:
                    self.category = "L"
            elif splitstr[0][0] in "Dd":
                if splitstr[4][0] in "Aa":
                    self.category = "DA"
                elif splitstr[4][0] in "Ee":
                    self.category = "DE"
                elif splitstr[4][0] in "Mm":
                    self.category = "DM"
                else:
                    self.category = "D"
            else:
                raise NameError(f"Unrecognised category: {splitstr[0]}")
            splitdate = splitstr[1].split(FILE_DATE_SEPARATOR)
            if len(splitdate) >= 3:
                year = int(splitdate[0])
                if year < 2000:
                    year += 2000
                month = int(splitdate[1])
                day = int(splitdate[2])
            elif len(splitdate) == 2:
                year = datetime.datetime.now().year
                month = int(splitdate[0])
                day = int(splitdate[1])
            else:
                raise NameError(f"Incomplete date format: {splitdate}")
            starttime = splitstr[2].split(FILE_TIME_SEPARATOR)
            if len(starttime) == 3:
                starthour = int(starttime[0])
                startminute = int(starttime[1])
                startsecond = int(starttime[2])
            elif len(starttime) == 2:
                starthour = int(starttime[0])
                startminute = int(starttime[1])
                startsecond = 0
            else:
                raise NameError(f"Incomplete time format: {starttime}")
            stoptime = splitstr[3].split(FILE_TIME_SEPARATOR)
            if len(stoptime) == 3:
                stophour = int(stoptime[0])
                stopminute = int(stoptime[1])
                stopsecond = int(stoptime[2])
            elif len(stoptime) == 2:
                stophour = int(stoptime[0])
                stopminute = int(stoptime[1])
                stopsecond = 0
            else:
                raise NameError(f"Incomplete time format: {stoptime}")
            self.start = datetime.datetime(year, month, day, starthour, startminute, startsecond)
            self.stop = datetime.datetime(year, month, day, stophour, stopminute, stopsecond)
            if self.stop <= self.start:
                raise NameError(f"Stop time earlier than start time: {self.str()}")
            if len(splitstr) >= 5:
                self.comment = splitstr[4].strip("\n")
            else:
                self.comment = "N/A"
            print(f"New Slot: {self.str()}")
        else:
            raise NameError(f"Incomplete line: {splitstr}")

    def str(self, oneline = True):
        if self.category == "A":
            category_str = f"Accumulator"
        elif self.category == "E":
            category_str = f"Electrical "
        elif self.category == "M":
            category_str = f"Mechanical "
        elif self.category == "L":
            category_str = f"Lunch      "
        elif self.category == "LA":
            category_str = f"Lunch Accu "
        elif self.category == "LE":
            category_str = f"Lunch Elec "
        elif self.category == "LM":
            category_str = f"Lunch Mech "
        elif self.category == "D":
            category_str = f"Dinner     "
        elif self.category == "DA":
            category_str = f"Dinner Accu"
        elif self.category == "DE":
            category_str = f"Dinner Elec"
        elif self.category == "DM":
            category_str = f"Dinner Mech"
        if oneline:
            separator = " | "
            return(f"{category_str}{separator}Start: {self.start}{separator}Stop: {self.stop}{separator}Duration: {self.stop-self.start}{separator}{self.comment}")
        else:
            separator = "\n"
            return(f"Start: {self.start.strftime('%H:%M:%S')}{separator}Stop: {self.stop.strftime('%H:%M:%S')}{separator}Remaining: {str(self.stop-datetime.datetime.now()+datetime.timedelta(seconds=1)).split('.')[0]}{separator}{self.comment}")
class ScrutimerTimetable():
    
    def __init__(self):
        self.slot_list = []

    def add_slots(self, datastr):
        for s in datastr:
            if s[0] != "#":
                if len(s.split(FILE_SEPARATOR)) >= 4:
                    self.add_slot(slot_str = s, nocheck = True)
                else:
                    print(f"File: Incomplete line: {s}")
            else:
                print(f"File: Comment: {s.strip()}")
        self.check_slots()

    def add_slot(self, slot_str, nocheck = False):
        s = Slot(slot_str)
        self.slot_list.append(s)
        if nocheck == False:
            self.check_slots()

    def check_slots(self):
        for s1 in self.slot_list:
            for s2 in self.slot_list:
                if (s1 != s2) & (s1.category == s2.category):
                    if ((s1.start >= s2.start) & (s1.start <= s2.stop)) | ((s1.stop >= s2.start) & (s1.stop <= s2.stop)):
                        raise NameError(f"Overlapping slots: \n{s1.str(oneline=True)}\n{s2.str(oneline=True)}")

    def current_slot(self, category):
        slot_str = "Currently no slot"
        for s in self.slot_list:
            if s.category == category:
                if (s.start <= datetime.datetime.now()) and (s.stop >= datetime.datetime.now()):
                    slot_str = s.str(oneline = False)
        if "Currently no slot" in slot_str:
            next_slot_initial = datetime.datetime(2050,12,12,23,59)
            next_slot_start = next_slot_initial
            next_slot = self.slot_list[0]
            for s in self.slot_list:
                if s.category == category:
                    if (s.start > datetime.datetime.now()) & (s.start < next_slot_start):
                        next_slot_start = s.start
                        next_slot = s
                        slot_str = s.str(oneline = False)
            if next_slot_start < next_slot_initial:
                slot_str = f"Currently no slot\nNext Slot: {next_slot.start}"
                #slot_str = f"Currently no slot\nNext Slot: {next_slot.start.strftime('%H:%M:%S')}"
        return slot_str
        
        
    def UpdateAnnouncement(self):
        announcement_list = []
        for s in self.slot_list:
            if ((s.announce_5_min == False) and (s.stop-datetime.timedelta(minutes=5, seconds=2) <= datetime.datetime.now()) and (s.stop-datetime.timedelta(minutes=5) >= datetime.datetime.now())):
                s.announce_5_min = True
                announcement_list.append([s.category, "5_min"])
                continue
            if ((s.announce_over == False) and (s.stop<= datetime.datetime.now()) and (s.stop+datetime.timedelta(seconds=2)>= datetime.datetime.now())):
                s.announce_over = True
                announcement_list.append([s.category, "over"])
        return announcement_list
    


def AddAnnouncements():
    list = fsg_timetable.UpdateAnnouncement()
    for s in list:
        announcements.AddAnnouncement(s[0],s[1])

# Define our backend object, which we pass to QML.
backend = Backend()
announcements = ScrutimerAnnouncement()
announcements.Start()
engine.rootObjects()[0].setProperty('backend', backend)

# Read scrutineering time table
file = open(FILE_NAME, "r")
content = file.readlines()
file.close()
#print(content)
fsg_timetable = ScrutimerTimetable()
fsg_timetable.add_slots(content)

# Initial call to trigger first update. Must be after the setProperty to connect signals.
backend.update_time()

# Define timer.
UpdateTimer= QTimer()
UpdateTimer.setInterval(1000)  # msecs 100 = 1/10th sec
UpdateTimer.timeout.connect(AddAnnouncements)
UpdateTimer.start()
        

sys.exit(app.exec())

