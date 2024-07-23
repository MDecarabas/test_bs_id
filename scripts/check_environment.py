#!/usr/bin/env python

"""
configure the Bluesky framework
"""

from aps_8id_bs_instrument.tests.check_subnet import warn_if_not_aps_controls_subnet
from aps_8id_bs_instrument.tests.check_dm import check_dm

warn_if_not_aps_controls_subnet()
check_dm()
