
import numpy as np
import georinex 
import logging
from gps_time import GPSTime
from datetime import datetime
from configparser import ConfigParser

from navy.misc.enumerations import GNSSSystems
from navy.io.gnssdata import ObservationData, NavigationData
from navy.space.ephemeris import BRDCEphemeris

# =====================================================================================================================

class RINEXObs(ObservationData):

    config : ConfigParser

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, config:ConfigParser):

        self.config = config

        return
    
    # -----------------------------------------------------------------------------------------------------------------

    def read(self, filepath):
        logging.getLogger(__name__).info(f"Importing file ({filepath})")

        # Define selectors
        signals = self._getSignals()
        systems = self._getSytems()
        start_time = datetime.strptime(self.config.get("PROCESSING", "start_time"), '%Y-%m-%dT%H:%M:%S')
        stop_time  = datetime.strptime(self.config.get("PROCESSING", "stop_time"), '%Y-%m-%dT%H:%M:%S')

        # Load file
        self.data = georinex.load(filepath, tlim=[start_time, stop_time], meas=signals, use=systems)

        return
    
    # -----------------------------------------------------------------------------------------------------------------

    def getData(self, time, signal):

        data = self.data[signal].sel(time=[time]).values
        sats = self.data[signal].sel(time=[time]).coords["sv"].values

        return data, sats
    
    # -----------------------------------------------------------------------------------------------------------------

    def _getSignals(self):

        signals_config = list(self.config.get("DEFAULT", "signals").split(","))

        signals = []
        for sig in signals_config:
            signals += [f"C{sig}", f"L{sig}", f"D{sig}", f"S{sig}"]

        return signals
    
    # -----------------------------------------------------------------------------------------------------------------

    def _getSytems(self):

        systems = set(self.config.get("DEFAULT", "systems").split(","))

        return systems

# =====================================================================================================================

class RINEXNav(NavigationData):

    config : ConfigParser

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, config:ConfigParser):

        self.config = config

        return
    
    # -----------------------------------------------------------------------------------------------------------------

    def read(self, filepath):
        logging.getLogger(__name__).info(f"Importing file ({filepath})")

        # Define selectors
        systems = self._getSytems()

        # Load file
        self.data = georinex.load(filepath, use=systems)

        return
    
    # -----------------------------------------------------------------------------------------------------------------

    def getSatellitesPositions(self, time, prn:list):

        satpos = np.empty((len(prn), 3))
        satclock = np.empty(len(prn))
        i = 0
        for sat in prn:

            # Retrieve ephemeris
            try:
                data = self.data.sel(sv=sat).dropna(dim="time", how="any").sel(time=time, method="pad")
            except:
                continue
            
            toc = GPSTime.from_datetime(datetime.utcfromtimestamp(data.time.values.tolist()/1e9)).seconds
            eph = BRDCEphemeris()
            eph.fromXArray(data, toc)

            # Compute positions
            tow = GPSTime.from_datetime(time).seconds
            pos, clock = eph.computePosition(tow)
            satpos[i, :] = pos
            satclock[i] = clock
            i += 1

        return
    
    # -----------------------------------------------------------------------------------------------------------------

    def _getSytems(self):

        systems = set(self.config.get("DEFAULT", "systems").split(","))

        return systems
    
# =====================================================================================================================