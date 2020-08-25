"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.config import ConfigurationError
from byceps.util.system import (
    get_config_filename_from_env,
    get_config_filename_from_env_or_exit,
    get_env_value,
)


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


# -------------------------------------------------------------------- #


def test_get_config_filename_from_env_with_value(monkeypatch):
    monkeypatch.setenv('BYCEPS_CONFIG', 'site01_prod')

    assert get_config_filename_from_env() == 'site01_prod'


def test_get_config_filename_from_env_without_value():
    with pytest.raises(ConfigurationError) as excinfo:
        get_config_filename_from_env()

    assert str(excinfo.value) == (
        "No configuration file was specified via the 'BYCEPS_CONFIG' "
        'environment variable.'
    )


# -------------------------------------------------------------------- #


def test_get_config_filename_from_env_or_exit_with_value(monkeypatch):
    monkeypatch.setenv('BYCEPS_CONFIG', 'site01_prod')

    assert get_config_filename_from_env_or_exit() == 'site01_prod'


def test_get_config_filename_from_env_or_exit_without_value():
    with pytest.raises(SystemExit) as excinfo:
        get_config_filename_from_env_or_exit()

    assert excinfo.value.code == 1
