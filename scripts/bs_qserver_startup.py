"""
Configure for data collection using bluesky-queueserver.
"""

import logging
import os

import ophyd
import pyRestTable

from sim_bs_instrument.callbacks import *  # noqa
from sim_bs_instrument.devices import *  # noqa
from sim_bs_instrument.initialize_bs_tools import RE
from sim_bs_instrument.initialize_bs_tools import cat
from sim_bs_instrument.plans import *  # noqa
from sim_bs_instrument.utils.iconfig_loader import iconfig

# guides choice of module to import cat

logger = logging.getLogger(__name__)

logger.info(__file__)
print(__file__)

RE.subscribe(cat.v1.insert)

ophyd.set_cl(iconfig.get("OPHYD_CONTROL_LAYER", "PyEpics").lower())
logger.info(f"using ophyd control layer: {ophyd.cl.name}")