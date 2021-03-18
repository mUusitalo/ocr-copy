import screeninfo

from pos2 import Pos2

class Monitor(screeninfo.Monitor):
    def has_pos(self, pos):
        return ((self.x <= pos.x <= self.x + self.width)
                and (self.y <= pos.y <= self.y + self.height))

class MonitorHandler:
    monitors = []
    active_monitor = None

    @classmethod
    def update_monitors(cls):
        cls.monitors = [Monitor(m.x, m.y, m.width, m.height) for m in screeninfo.get_monitors()]

    @classmethod
    def find_new_monitor(cls, pos): #Called by update_active_monitor. Finds active monitor based on list of monitors and a position (the cursor's position)
        if cls.active_monitor and cls.active_monitor.has_pos(pos): return cls.active_monitor # It's unnecessary to go further if the cursor is on self.monitor
        tries = 0
        while tries <= 1:
            for monitor in cls.monitors:
                if monitor.has_pos(pos):
                    cls.active_monitor = monitor
                    print("Updated active monitor to " + str(monitor))
                    return monitor
            cls.update_monitors() #Goes this far if none of the monitors matched
            tries += 1
        raise Exception(f"Couldn't find cursor on any monitor in {tries} tries") #If none of the listed monitors matched even after updating the list