"""
byceps.util.upload
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path
from shutil import copyfileobj
from typing import Any, IO


def store(source: IO[Any], target_path: Path) -> None:
    """Copy source data to the target path."""
    if target_path.exists():
        raise FileExistsError

    with target_path.open('wb') as f:
        copyfileobj(source, f)


def delete(path: Path) -> None:
    """Delete the path."""
    try:
        path.unlink()
    except OSError:
        pass
