import pkg_resources

from . import sim, utils, visualization
from .sim import *
from .utils import *
from .visualization import *

__version__ = pkg_resources.require("hypercontagion")[0].version
