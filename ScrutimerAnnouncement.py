import pygame
import queue
import time
import threading

class ScrutimerAnnouncement:

    _announcement_5_min = {"A":"Sounds/5_min_accu.mp3", 
                           "M":"Sounds/5_min_mech.mp3", 
                           "E":"Sounds/5_min_elec.mp3"}
    _announcement_term =  {"A":"Sounds/over_accu.mp3", 
                           "M":"Sounds/over_mech.mp3", 
                           "E":"Sounds/over_elec.mp3", 
                           "D":"Sounds/dinner.mp3", 
                           "L":"Sounds/lunch.mp3"}
    _announcements = {"5_min": _announcement_5_min, "over":_announcement_term}
    _announcementQueue = queue.Queue()
    
    def __init__(self):
        pygame.mixer.init()        
        
    def AddAnnouncement(self, category, time):
        ''' Add an announcement to the queue'''
        try:
            self._announcementQueue.put(self._announcements[time][category])
        except:
            print(F"No announcement found for category {category} with time {time}!")
            
    def Start(self):
        '''
        Launch a Thread to collect repetitively all measurements.
        '''
        self._RunActive = True
        # Create and start new Thread, such that GUI does not hang.
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def Stop(self):
        '''
        Stop the Permanent Run Loop
        '''
        self._RunActive = False
        if(self._thread is not None):
            self._thread.join()
    
    def _run(self):
        while(self._RunActive):
            if(self._announcementQueue.empty()):
               time.sleep(1) 
            else:
                pygame.mixer.music.load(self._announcementQueue.get())
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue 
                    
    def __del__(self):
        self.Stop()
                    
if __name__ == "__main__":

    Scruti = ScrutimerAnnouncement()
    Scruti.Start()
    txt = ""
    while (txt != "q"):
        Scruti.AddAnnouncement(txt, "5_min")
        txt = input("Add Announcement:")
        
    Scruti.Stop()
    