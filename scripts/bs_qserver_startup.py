"""
Configure for data collection using bluesky-queueserver.
"""

import logging

from sim_bs_instrument.callbacks import *  # noqa
from sim_bs_instrument.devices import *  # noqa
from sim_bs_instrument.initialize_bs_tools import RE
from sim_bs_instrument.initialize_bs_tools import cat
from sim_bs_instrument.plans import *  # noqa
from sim_bs_instrument.utils.epics_tools import set_control_layer

# guides choice of module to import cat

logger = logging.getLogger(__name__)

logger.info(__file__)
print(__file__)

RE.subscribe(cat.v1.insert)

set_control_layer("PyEpics")
