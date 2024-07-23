"""
configure for data collection in a console session
"""

from apstools.utils import *  # noqa

from .utils.iconfig_loader import iconfig
from .callbacks.spec_data_file_writer import specwriter
from .initialize_bs_tools import RE
from .devices import *  # noqa
from .plans import *  # noqa

## ipython helpers
from .utils.session_logs import logger

logger.info(__file__)
logger.info("#### data collection tools are loaded is complete. ####")
