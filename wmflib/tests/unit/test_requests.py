"""Requests module tests."""
from unittest import mock

import pytest

from requests import Request, Session

from wmflib import requests


def test_timeout_http_adapter_init_default():
    """If instantiated without any parameter the TimeoutHTTPAdapter should set the default timeout."""
    adapter = requests.TimeoutHTTPAdapter()
    assert adapter.timeout == requests.DEFAULT_TIMEOUT


def test_timeout_http_adapter_init_custom():
    """The TimeoutHTTPAdapter should use the given timeout, if specified."""
    adapter = requests.TimeoutHTTPAdapter(timeout=9.9)
    assert adapter.timeout == 9.9


@pytest.mark.parametrize('timeout, expected', (
    (None, requests.DEFAULT_TIMEOUT),
    (1.0, 1.0),
))
@mock.patch('wmflib.requests.HTTPAdapter.send', spec_set=True)
def test_timeout_http_adapter_send_default(mocked_send, timeout, expected):
    """Sending a request with the TimeoutHTTPAdapter should use the default timeout if not set."""
    adapter = requests.TimeoutHTTPAdapter()
    request = Request('GET', 'https://example.com/')
    prepared_request = request.prepare()
    if timeout:
        adapter.send(prepared_request, timeout=timeout)
    else:
        adapter.send(prepared_request)

    assert mocked_send.call_count == 1
    assert mocked_send.mock_calls[0][2].get('timeout') == expected


def test_session():
    """Calling session should return a Requests's session pre-configured."""
    session = requests.http_session('UA-name')
    assert isinstance(session, Session)
    assert 'UA-name' in session.headers['User-Agent']
