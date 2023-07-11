
import numpy as np
import xarray as xr

from navy.misc.enumerations import GNSSSystems
import navy.misc.constants as constants 

class BRDCEphemeris():
    systemID   : GNSSSystems
    satelliteID: int
    iode     : int
    iodc     : int
    toe      : float
    toc      : float
    tgd      : float
    af2      : float
    af1      : float
    af0      : float
    ecc      : float 
    sqrtA    : float
    crs      : float
    deltan   : float
    m0       : float
    cuc      : float
    cus      : float
    cic      : float
    omega0   : float
    cis      : float
    i0       : float
    crc      : float
    omega    : float
    omegaDot : float
    iDot     : float
    ura      : float
    health   : float

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):

        return
    
    # ----------------------------------------------------------------------------------------------------------------
    
    def fromXArray(self, xarray:xr.DataArray, toc : float):

        self.satelliteID = str(xarray.coords['sv'].values)
        self.iode        = int(xarray['IODE'].values)
        self.iodc        = int(xarray['IODC'].values)
        self.toe         = int(xarray['Toe'].values)
        self.toc         = toc
        self.tgd         = float(xarray['TGD'].values)
        self.af2         = float(xarray['SVclockDriftRate'].values)
        self.af1         = float(xarray['SVclockDrift'].values)
        self.af0         = float(xarray['SVclockBias'].values)
        self.ecc         = float(xarray['Eccentricity'].values)
        self.sqrtA       = float(xarray['Eccentricity'].values)
        self.crs         = float(xarray['Crs'].values)
        self.deltan      = float(xarray['DeltaN'].values)
        self.m0          = float(xarray['M0'].values)
        self.cuc         = float(xarray['Cuc'].values)
        self.cus         = float(xarray['Cus'].values)
        self.cic         = float(xarray['Cic'].values)
        self.omega0      = float(xarray['Omega0'].values)
        self.cis         = float(xarray['Cis'].values)
        self.i0          = float(xarray['Io'].values)
        self.crc         = float(xarray['Crc'].values)
        self.omega       = float(xarray['omega'].values)
        self.omegaDot    = float(xarray['OmegaDot'].values)
        self.iDot        = float(xarray['IDOT'].values)
        self.ura         = float(xarray['SVacc'].values)
        self.health      = float(xarray['health'].values)

        return
    
    # ----------------------------------------------------------------------------------------------------------------

    def computePosition(self, time : float):

        # Compute difference between current time and orbit reference time
        # Check for week rollover at the same time
        dt = self.timeCheck(time - self.toc)

        # Find the satellite clock correction and apply
        satClkCorr = (self.af2 * dt + self.af1) * dt + self.af0
        time -= satClkCorr

        # Orbit computations
        tk = self.timeCheck(time - self.toe)
        a  = self.sqrtA * self.sqrtA
        n0 = np.sqrt(constants.EARTH_GM / a ** 3)
        n  = n0 + self.deltan
        
        ## Eccentricity computation
        M = self.m0 + n * tk
        M = np.remainder(M + 2 * constants.PI, 2 * constants.PI)
        E = M
        for i in range(10):
            E_old = E
            E = M + self.ecc * np.sin(E)
            dE = np.remainder(E - E_old, 2 * constants.PI)
            if abs(dE) < 1e-12:
                break
        E = np.remainder(E + 2 * constants.PI, 2 * constants.PI)
        
        dtr = constants.RELATIVIST_CLOCK_F * self.ecc * self.sqrtA * np.sin(E)
        nu = np.arctan2(np.sqrt(1 - self.ecc ** 2) * np.sin(E), np.cos(E) - self.ecc)
        phi = np.remainder(nu + self.omega, 2 * constants.PI)

        u = phi + self.cuc * np.cos(2 * phi) + self.cus * np.sin(2 * phi)
        r = a * (1 - self.ecc * np.cos(E)) + self.crc * np.cos(2 * phi) + self.crs * np.sin(2 * phi)
        i = self.i0 + self.iDot * tk + self.cic * np.cos(2 * phi) + self.cis * np.sin(2 * phi)
        
        Omega = self.omega0 + (self.omegaDot - constants.EARTH_ROTATION_RATE) * tk \
            - constants.EARTH_ROTATION_RATE * self.toe
        Omega = np.remainder(Omega + 2 * constants.PI, 2 * constants.PI)
        
        satellitePosition = np.zeros(3)
        satellitePosition[0] = np.cos(u)*r*np.cos(Omega) - np.sin(u)*r*np.cos(i)*np.sin(Omega)
        satellitePosition[1] = np.cos(u)*r*np.sin(Omega) + np.sin(u)*r*np.cos(i)*np.cos(Omega)
        satellitePosition[2] = np.sin(u)*r*np.sin(i)
        self.lastPosition = satellitePosition

        satelliteClockCorrection = (self.af2*dt + self.af1)*dt + self.af0 - dtr

        # TODO Satellite velocity

        return satellitePosition, satelliteClockCorrection
    
    # -----------------------------------------------------------------------------------------------------------------

    def timeCheck(self, time):
        """ 
        timeCheck accounting for beginning or end of week crossover.
        corrTime = check_t(time);
          Inputs:
              time        - time in seconds
          Outputs:
              corrTime    - corrected time (seconds)
        Kai Borre 04-01-96
        Copyright (c) by Kai Borre
        """
        half_week = 302400.0
        corrTime = time

        if time > half_week:
            corrTime = time - 2 * half_week
        elif time < - half_week:
            corrTime = time + 2 * half_week
        
        return corrTime