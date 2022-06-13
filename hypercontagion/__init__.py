import pkg_resources

from . import sim, utils
from .sim import *
from .utils import *

__version__ = pkg_resources.require("hypercontagion")[0].version
