# -*- coding: utf-8 -*-

import sys

try:
    from byceps.application_factory import app
except Exception as e:
    sys.stderr.write("{}\n".format(e))
    sys.exit()
