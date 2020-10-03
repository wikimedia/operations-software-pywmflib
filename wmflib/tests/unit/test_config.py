"""Config module tests."""

import configparser

from logging import DEBUG

import pytest

from wmflib.config import load_ini_config, load_yaml_config
from wmflib.exceptions import WmflibError
from wmflib.tests import check_logs, get_fixture_path, require_caplog


def test_load_yaml_config_empty():
    """Loading an empty config should return an empty dictionary."""
    config_dict = load_yaml_config(get_fixture_path('config', 'empty.yaml'))
    assert {} == config_dict


@pytest.mark.parametrize('name, message', (
    ('invalid.yaml', 'ParserError'),
    ('non-existent.yaml', 'FileNotFoundError'),
))
def test_load_yaml_config_raise(name, message):
    """Loading an invalid config should raise Exception."""
    with pytest.raises(WmflibError, match=message):
        load_yaml_config(get_fixture_path('config', name))


@require_caplog
@pytest.mark.parametrize('name', ('invalid.yaml', 'non-existent.yaml'))
def test_load_yaml_config_no_raise(caplog, name):
    """Loading an invalid config with raises=False should return an empty dictionary."""
    with caplog.at_level(DEBUG):
        config_dict = load_yaml_config(get_fixture_path('config', name), raises=False)

    assert {} == config_dict
    check_logs(caplog, 'Could not load config file', DEBUG)


def test_load_yaml_config_valid():
    """Loading a valid config should return its content."""
    config_dir = get_fixture_path('config', 'valid.yaml')
    config_dict = load_yaml_config(config_dir)
    assert 'key' in config_dict


def test_load_ini_config():
    """Loading a INI config should return a configparser.ConfigParser object."""
    config = load_ini_config(get_fixture_path('config', 'config.ini'))
    assert isinstance(config, configparser.ConfigParser)
    assert config.defaults()['key'] == 'value'


@pytest.mark.parametrize('message', 'File contains no section headers')
def test_load_invalid_ini_config(message):
    """Loading an invalid INI config should raise an exception."""
    with pytest.raises(WmflibError, match=message):
        load_ini_config(get_fixture_path('config', 'invalid.ini'))


@require_caplog
def test_load_invalid_ini_config_no_raise(caplog):
    """Loading an invalid config with raises=False should return an empty ConfigParser."""
    with caplog.at_level(DEBUG):
        config = load_ini_config(get_fixture_path('config', 'invalid.ini'), raises=False)

    assert configparser.ConfigParser() == config
    check_logs(caplog, 'Could not load config file', DEBUG)
