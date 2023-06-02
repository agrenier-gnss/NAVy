from abc import ABC, abstractmethod

# =====================================================================================================================

class ObservationData(ABC):
    
    def __init__(self):
        return
    
    @abstractmethod
    def getData(self):
        return
    
# =====================================================================================================================

class NavigationData(ABC):

    def __init__(self):
        return
    
    @abstractmethod
    def getSatellitesPositions():
        return
