"""
Configure for data collection using bluesky-queueserver.
"""

import logging

import databroker
from sim_bs_instrument.callbacks import *  # noqa
from sim_bs_instrument.devices import *  # noqa
from sim_bs_instrument.plans import *  # noqa
from sim_bs_instrument.utils.catalog import load_catalog
from sim_bs_instrument.utils.epics_tools import set_control_layer
from sim_bs_instrument.utils.iconfig_loader import iconfig
from sim_bs_instrument.utils.run_engine import run_engine

# guides choice of module to import cat

logger = logging.getLogger(__name__)

logger.info(__file__)
print(__file__)

# Connect with our mongodb database
catalog_name = iconfig.get("DATABROKER_CATALOG", "training")
try:
    # We don't actually run this part because it is unable to find a yaml corresponding to the catalog name. For this to execute the yaml has to be store in:
    # import databroker; print(databroker.catalog_search_path())
    # https://blueskyproject.io/databroker/reference/configuration.html?highlight=search%20path
    cat = load_catalog(catalog_name)
    logger.info("using databroker catalog '%s'", cat.name)
except KeyError:
    cat = databroker.temp().v2
    logger.info("using TEMPORARY databroker catalog '%s'", cat.name)

# Set up a RunEngine.
RE = run_engine()

set_control_layer("PyEpics")
