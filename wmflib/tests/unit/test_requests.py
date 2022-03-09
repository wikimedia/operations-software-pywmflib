"""Requests module tests."""
from unittest import mock

import pytest

from requests import Request, Session

from wmflib import requests


def test_timeout_http_adapter_init_default():
    """If instantiated without any parameter the TimeoutHTTPAdapter should set the default timeout."""
    adapter = requests.TimeoutHTTPAdapter()
    assert adapter.timeout == requests.DEFAULT_TIMEOUT


@pytest.mark.parametrize('timeout', (9.9, (1.1, 9.9)))
def test_timeout_http_adapter_init_custom(timeout):
    """The TimeoutHTTPAdapter should use the given timeout, if specified."""
    adapter = requests.TimeoutHTTPAdapter(timeout=timeout)
    assert adapter.timeout == timeout


@pytest.mark.parametrize('timeout, expected', (
    (None, (None, None)),
    ((None, None), (None, None)),
    ('NOTSET', requests.DEFAULT_TIMEOUT),
    (1.0, (1.0, 1.0)),
    ((1.1, 9.9), (1.1, 9.9))
))
@mock.patch('urllib3.connectionpool.HTTPConnectionPool.urlopen', spec_set=True)
def test_timeout_http_adapter_send(mocked_send, timeout, expected):
    """Sending a request with the TimeoutHTTPAdapter should use the default timeout."""
    if timeout == 'NOTSET':
        adapter = requests.TimeoutHTTPAdapter()
    else:
        adapter = requests.TimeoutHTTPAdapter(timeout=timeout)

    request = Request('GET', 'https://example.com/')
    prepared_request = request.prepare()
    adapter.send(prepared_request)

    assert mocked_send.call_count == 1
    used_timeout = mocked_send.mock_calls[0][2].get('timeout')
    assert used_timeout.connect_timeout == expected[0]
    assert used_timeout.read_timeout == expected[1]


@pytest.mark.parametrize('timeout, expected', (
    (None, (2.2, 6.6)),
    ((None, None), (None, None)),
    (1.0, (1.0, 1.0)),
    ((1.1, 9.9), (1.1, 9.9))
))
@mock.patch('urllib3.connectionpool.HTTPConnectionPool.urlopen', spec_set=True)
def test_timeout_http_adapter_send_override(mocked_send, timeout, expected):
    """Sending a request with the TimeoutHTTPAdapter and timeout set should use the override unless is None."""
    adapter = requests.TimeoutHTTPAdapter(timeout=(2.2, 6.6))

    request = Request('GET', 'https://example.com/')
    prepared_request = request.prepare()
    adapter.send(prepared_request, timeout=timeout)

    assert mocked_send.call_count == 1
    used_timeout = mocked_send.mock_calls[0][2].get('timeout')
    assert used_timeout.connect_timeout == expected[0]
    assert used_timeout.read_timeout == expected[1]


def test_session_default_codes_methods():
    """Calling session should return a Requests's session pre-configured with the default methods and codes."""
    session = requests.http_session('UA-name')
    assert session.adapters['https://'].max_retries.status_forcelist == requests.DEFAULT_RETRY_STATUS_CODES
    param_name = 'allowed_methods' if hasattr(requests.Retry.DEFAULT, 'allowed_methods') else 'method_whitelist'
    assert getattr(session.adapters['https://'].max_retries, param_name) == requests.DEFAULT_RETRY_METHODS


def test_session_custom_codes_methods():
    """Calling session with custom status codes and methods, should return a Requests's session with those values."""
    session = requests.http_session('UA-name', retry_codes=(429,), retry_methods=('GET',))
    assert session.adapters['https://'].max_retries.status_forcelist == (429,)
    param_name = 'allowed_methods' if hasattr(requests.Retry.DEFAULT, 'allowed_methods') else 'method_whitelist'
    assert getattr(session.adapters['https://'].max_retries, param_name) == ('GET',)


def test_session():
    """Calling session should return a Requests's session pre-configured."""
    session = requests.http_session('UA-name')
    assert isinstance(session, Session)
    assert 'UA-name' in session.headers['User-Agent']
