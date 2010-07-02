from mom.Collectors.Collector import *

class GuestQemuProc(Collector):
    """
    This Collector returns statistics for the qemu process representing a guest.
        host_minor_faults - The number of host minor faults a guest's qemu
                            process caused since the last collection.
        host_major_faults - The number of host major faults a guest's qemu
                            process caused since the last collection.
            NOTE: Host major faults generally require host disk IO to satisfy,
                  host minor faults do not.
        rss - The resident set size counts the number of resident pages
              associated with this qemu process.
    """
    def __init__(self, properties):
        self.pid = properties['pid']
        self.pid_stat_file = None
        if self.pid is not None:
            self.pid_stat_file = open_datafile("/proc/" + str(self.pid) + "/stat")
        self.prev_minor_faults = None
        self.prev_major_faults = None

    def __del__(self):
        if self.pid_stat_file is not None:
            self.pid_stat_file.close()

    def collect(self):
        if self.pid_stat_file is None:
            return {}

        # Only report the change in these statistics since the last collection
        self.pid_stat_file.seek(0)
        try:
            stats = self.pid_stat_file.read().split()
        except IOError, (errno, strerror):
            raise CollectionError("Cannot read stat file: %s" % strerror)
        cur_minor_faults = int(stats[9])
        cur_major_faults = int(stats[11])
        rss = int(stats[23])
        if self.prev_minor_faults is None:
            self.prev_minor_faults = cur_minor_faults
        if self.prev_major_faults is None:
            self.prev_major_faults = cur_major_faults
        minor_faults = cur_minor_faults - self.prev_minor_faults
        self.prev_minor_faults = cur_minor_faults
        major_faults = cur_major_faults - self.prev_major_faults
        self.prev_major_faults = cur_major_faults

        return { 'host_minor_faults': minor_faults, 'host_major_faults': major_faults, 'rss': rss }
        
    def getFields(self=None):
        return set(['host_minor_faults', 'host_major_faults', 'rss'])

def instance(properties):
    return GuestQemuProc(properties)