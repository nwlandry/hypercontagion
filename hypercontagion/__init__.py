import pkg_resources

from hypercontagion import simulation
from hypercontagion.simulation import *

__version__ = pkg_resources.require("hypercontagion")[0].version
