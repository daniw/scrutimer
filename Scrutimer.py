# Analog clock based on example: 
# https://doc.qt.io/qt-6/qtqml-syntax-basics.html
import sys

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from time import strftime, localtime

FILE_SEPARATOR = ";"
FILE_NAME = "Scrutimer.tbl"

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
            self.start = f"{splitstr[1]} {splitstr[2]}"
            stoptime = splitstr[3].strip("\n")
            self.stop = f"{splitstr[1]} {stoptime}"
            if len(splitstr) >= 5:
                self.comment = splitstr[4].strip("\n")
            else:
                self.comment = "N/A"
            print(f"New Slot: {self.str()}")
        else:
            raise NameError(f"Incomplete line: {splitstr}")

    def str(self):
        return(f"{self.category} {self.start} {self.stop} {self.comment}")

class Timetable():
    slot_list = {}

    def __init__(self):
        self.slot_list = {}

    def add_slots(self, datastr):
        for s in datastr:
            if s[0] != "#":
                if len(s.split(FILE_SEPARATOR)) >= 4:
                    self.add_slot(s)
                else:
                    print(f"File: Incomplete line: {s}")
            else:
                print(f"File: Comment: {s.strip()}")

    def add_slot(self, datastr):
        s = Slot(datastr)
        self.slot_list = [self.slot_list, s]

# Define our backend object, which we pass to QML.
#backend = Backend()

#engine.rootObjects()[0].setProperty('backend', backend)

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

