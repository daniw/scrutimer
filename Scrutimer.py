# Analog clock based on example: 
# https://doc.qt.io/qt-6/qtqml-syntax-basics.html
import sys
import datetime

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from time import strftime, localtime

FILE_NAME = "Scrutimer.tbl"
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

class Slot():
    category = ""
    start = ""
    stop = ""
    comment = ""

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
        if oneline:
            separator = " | "
        else:
            separator = "\n"
        return(f"{category_str}{separator}Start: {self.start}{separator}Stop: {self.stop}{separator} Duration: {self.stop-self.start}{separator}{self.comment}")

class Timetable():
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

# Define our backend object, which we pass to QML.
backend = Backend()

engine.rootObjects()[0].setProperty('backend', backend)

# Read scrutineering time table
file = open(FILE_NAME, "r")
content = file.readlines()
file.close()
print(content)
fsg_timetable = Timetable()
fsg_timetable.add_slots(content)

# Initial call to trigger first update. Must be after the setProperty to connect signals.
backend.update_time()

sys.exit(app.exec())

