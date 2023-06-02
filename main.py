
from navy.io.rinex import RINEXObs, RINEXNav
from navy.positioning.spp import SinglePointPositioning
from configparser import ConfigParser

# Import configuration
config = ConfigParser()
config.read(".config/GPS_L1.ini")

# Import RINEX
rinexObs = RINEXObs(config)
rinexObs.read(config["FILES"]["filepath_obs"])
rinexNav = RINEXNav(config)
rinexNav.read(config["FILES"]["filepath_nav"])

# Processing
spp = SinglePointPositioning(config)
spp.obs = rinexObs
spp.nav = rinexNav
spp.run()

print("Hello World!")