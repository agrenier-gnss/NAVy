
from datetime import datetime, timedelta

from navy.misc.enumerations import FileType
from navy.io.gnssdata import ObservationData, NavigationData

class Positioning():
    
    obs : ObservationData
    nav : NavigationData

    def __init__(self):
        
        return

# =====================================================================================================================

class SinglePointPositioning(Positioning):

    def __init__(self, config):

        self.config = config
        
        self.start_time = datetime.strptime(self.config.get("PROCESSING", "start_time"), '%Y-%m-%dT%H:%M:%S')
        self.stop_time  = datetime.strptime(self.config.get("PROCESSING", "stop_time"), '%Y-%m-%dT%H:%M:%S')
        self.step_time  = timedelta(seconds=self.config.getint("PROCESSING", "step_time"))

        self.signals = list(self.config.get("DEFAULT", "signals").split(","))

        return
    
    # -----------------------------------------------------------------------------------------------------------------
    
    def run(self):
        
        time_list = [self.start_time]
        time_list += [self.start_time + self.step_time for x in range(0, (self.stop_time-self.start_time).seconds)]
        for time in time_list:
            
            # Get measurements
            for sig in self.signals:
                pseudoranges, satellites_prn = self.obs.getData(time, f"C{sig}") # pseudorange

                self.nav.getSatellitesPositions(time, satellites_prn)


        return
    
    # -----------------------------------------------------------------------------------------------------------------
    
    def _buildMatrices(self):



        return
    
# =====================================================================================================================
