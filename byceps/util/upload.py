"""
byceps.util.upload
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path
from shutil import copyfileobj
from typing import Any, IO


def store(
    source: IO[Any],
    target_path: Path,
    *,
    create_parent_path_if_nonexistant: bool = False,
) -> None:
    """Copy source data to the target path."""
    if target_path.exists():
        raise FileExistsError

    if create_parent_path_if_nonexistant:
        _create_path_if_nonexistant(target_path.parent)

    with target_path.open('wb') as f:
        copyfileobj(source, f)


def delete(path: Path) -> None:
    """Delete the path."""
    try:
        path.unlink()
    except OSError:
        pass


def _create_path_if_nonexistant(path: Path) -> None:
    """Create the path (and its parent paths) if it does not exist."""
    if not path.exists():
        path.mkdir(parents=True)
