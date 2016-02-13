# -*- coding: utf-8 -*-

"""
byceps.util.upload
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from shutil import copyfileobj


def store(source, target_path):
    """Copy source data to the target path."""
    if target_path.exists():
        raise FileExistsError

    with target_path.open('wb') as f:
        copyfileobj(source, f)


def delete(path):
    """Delete the path."""
    try:
        path.unlink()
    except OSError:
        pass
