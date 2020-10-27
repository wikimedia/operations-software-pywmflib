"""Requests module."""
from typing import Any

from requests import PreparedRequest, Response, Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # pylint: disable=import-error

from wmflib import __version__


DEFAULT_TIMEOUT: float = 5.0
""":py:class:`float`: the default timeout to use if none is passed, in seconds."""


class TimeoutHTTPAdapter(HTTPAdapter):
    """Requests HTTP Adapter with default timeout for all requests.

    See Also:
        https://hodovi.ch/blog/advanced-usage-python-requests-timeouts-retries-hooks/

    """

    def __init__(self, **kwargs: Any):
        """Initialize the adapter with a default timeout, that can be overriden.

        To override the default timeout of :py:const:`wmflib.requests.DEFAULT_REQUESTS_TIMEOUT`` pass the ``timeout``
        parameter when initializing an instance of this class.

        Params:
            As required by requests's HTTPAdapter:
            https://2.python-requests.org/en/master/api/#requests.adapters.HTTPAdapter

        """
        self.timeout = DEFAULT_TIMEOUT
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']
            del kwargs['timeout']

        super().__init__(**kwargs)

    def send(self, request: PreparedRequest,  # type: ignore # pylint: disable=arguments-differ
             **kwargs: Any) -> Response:
        """Override the send method to pass the default timeout if not set.

        Params:
            As required by requests's HTTPAdapter:
            https://2.python-requests.org/en/master/api/#requests.adapters.HTTPAdapter.send
            The ``noqa`` is needed unless the exact signature is replicated.

        """
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        return super().send(request, **kwargs)


def http_session(name: str, *, timeout: float = DEFAULT_TIMEOUT, tries: int = 3, backoff: float = 1.0) -> Session:
    """Return a new requests Session with User-Agent, default timeout and retry logic on failure already setup.

    The returned session will retry any ``DELETE, GET, HEAD, OPTIONS, PUT, TRACE`` request that returns one of
    the following HTTP status code:

        - 429 Too Many Requests
        - 500 Internal Server Error
        - 502 Bad Gateway
        - 503 Service Unavailable
        - 504 Gateway Timeout

    It will also retry any request that times out before the specified timeout. For non-idempotent HTTP methods the
    request will not be retried if the data has reached the server.

    The retry interval between requests is determined by the ``backoff`` parameter, see below.

    The timeout functionality is provided via the :py:class:`wmflib.requests.TimeoutHTTPAdapter` and individual request
    can override the session timeout by specifying a ``timeout`` parameter.

    See Also:
        https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry

    Arguments:
        name (str): the name to use for the User-Agent header. It can be specified in the ``name/version`` format, if
            applicable. The resulting header will be set to::

                pywmflib/{version} {name} +https://wikitech.wikimedia.org/wiki/Python/Wmflib root@wikimedia.org
        timeout (float): the default timeout to use in all requests within this session, in seconds. Any request can
            override it passing the ``timeout`` parameter explicitely.
        tries (int): the total number of requests to perform before bailing out.
        backoff (float): the backoff factor to use, will generate a sleep between retries, in seconds, of::

            {backoff factor} * (2 ** ({number of total retries} - 1))

    Returns:
        requests.Session: the pre-configured session.

    """
    retry_strategy = Retry(total=tries, backoff_factor=backoff, status_forcelist=[429, 500, 502, 503, 504])
    adapter = TimeoutHTTPAdapter(timeout=timeout, max_retries=retry_strategy)
    session = Session()
    user_agent = 'pywmflib/{version} {name} +https://wikitech.wikimedia.org/wiki/Python/Wmflib'.format(
        version=__version__, name=name)
    session.headers.update({'User-Agent': user_agent})
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
