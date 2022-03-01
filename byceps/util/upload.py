"""
byceps.util.upload
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path
from shutil import copyfileobj
from typing import Any, IO


def store(
    source: IO[Any],
    target_path: Path,
    *,
    create_parent_path_if_nonexistent: bool = False,
) -> None:
    """Copy source data to the target path."""
    if target_path.exists():
        raise FileExistsError

    if create_parent_path_if_nonexistent:
        _create_path_if_nonexistent(target_path.parent)

    with target_path.open('wb') as f:
        copyfileobj(source, f)


def delete(path: Path) -> None:
    """Delete the path."""
    try:
        path.unlink()
    except OSError:
        pass


def _create_path_if_nonexistent(path: Path) -> None:
    """Create the path (and its parent paths) if it does not exist."""
    if not path.exists():
        path.mkdir(parents=True)
