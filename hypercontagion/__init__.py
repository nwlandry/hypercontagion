import pkg_resources

from . import simulation
from .simulation import *

__version__ = pkg_resources.require("hypercontagion")[0].version
