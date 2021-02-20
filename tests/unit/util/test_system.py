"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.config import ConfigurationError
from byceps.util.system import get_env_value


def test_get_env_value_with_value(monkeypatch):
    monkeypatch.setenv('LAUNCH_CODE', '3-2-1-LIFT-OFF')

    actual = get_env_value('LAUNCH_CODE', 'Invalid launch code')

    assert actual == '3-2-1-LIFT-OFF'


def test_get_env_value_with_empty_value(monkeypatch):
    monkeypatch.setenv('LAUNCH_CODE', '')

    with pytest.raises(ConfigurationError) as excinfo:
        get_env_value('LAUNCH_CODE', 'Invalid launch code')

    assert str(excinfo.value) == 'Invalid launch code'


def test_get_env_value_without_value():
    with pytest.raises(ConfigurationError) as excinfo:
        get_env_value('LAUNCH_CODE', 'Invalid launch code')

    assert str(excinfo.value) == 'Invalid launch code'
