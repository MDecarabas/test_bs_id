"""
Configure for data collection using bluesky-queueserver.
"""

import logging
import os

import ophyd
import pyRestTable

from ..callbacks import *  # noqa
from ..devices import *  # noqa
from ..initialize_bs_tools import RE
from ..initialize_bs_tools import cat
from ..plans import *  # noqa
from ..utils.iconfig_loader import iconfig

# guides choice of module to import cat

logger = logging.getLogger(__name__)

logger.info(__file__)
print(__file__)

RE.subscribe(cat.v1.insert)

ophyd.set_cl(iconfig.get("OPHYD_CONTROL_LAYER", "PyEpics").lower())
logger.info(f"using ophyd control layer: {ophyd.cl.name}")


# update OS environment variables for APS Data Management
def _chop(text):
    return text.strip().split()[-1].split("=")


# fmt: off
_ev = {
    _chop(line)[0]: _chop(line)[-1]
    for line in open(iconfig["DM_SETUP_FILE"]).readlines()
    if line.startswith("export ")
}
os.environ.update(_ev)

def make_kv_table(data):
    '''make kv table'''
    table = pyRestTable.Table()
    table.labels = "key value".split()
    for k, v in sorted(data.items()):
        if isinstance(v, dict):
            table.addRow((k, make_kv_table(v)))
        else:
            table.addRow((k, v))
    return table


# if iconfig.get("WRITE_SPEC_DATA_FILES", False):
#     if specwriter is not None: # noqa
#         RE.subscribe(specwriter.receiver) # noqa
#         logger.info(f"writing to SPEC file: {specwriter.spec_filename}") # noqa
#         logger.info("   >>>>   Using default SPEC file name   <<<<")
#         logger.info("   file will be created when bluesky ends its next scan")
#         logger.info("   to change SPEC file, use command:   newSpecFile('title')")

# if iconfig.get("APS_IN_BASELINE", False):
#     sd.baseline.append(aps) # noqa #???
