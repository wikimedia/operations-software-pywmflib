"""Requests module."""
from typing import Any, Tuple, Union

from requests import PreparedRequest, Response, Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # pylint: disable=import-error

from wmflib import __version__


TypeTimeout = Union[float, Tuple[float, float]]
"""Type alias for the requests timeout parameter."""
DEFAULT_TIMEOUT: TypeTimeout = (3.0, 5.0)
""":py:const:`wmflib.requests.TypeTimeout`: the default timeout to use if none is passed, in seconds."""


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
        if kwargs.get('timeout') is None:  # The Session will pass timeout=None when not set by the caller.
            kwargs['timeout'] = self.timeout

        return super().send(request, **kwargs)


def http_session(name: str, *, timeout: TypeTimeout = DEFAULT_TIMEOUT, tries: int = 3,
                 backoff: float = 1.0) -> Session:
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
    can override the session timeout by specifying a ``timeout`` parameter. When using this adapter to unset the
    timeout for a specific call, it should be set to ``(None, None)``.

    Examples:
        With default parameters::

            from wmflib.requests import http_session
            session = http_session('AppName')  # The given name will be used in the User-Agent header, see below
            # At this point the session can be used as a normal requests session

        With customized parameters::

            session = http_session('AppName', timeout=10.0, tries=5, backoff=2.0)
            session = http_session('AppName', timeout=(3.0, 10.0), tries=5, backoff=2.0)

    See Also:
        https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry
        https://docs.python-requests.org/en/latest/user/advanced/#timeouts

    Arguments:
        name (str): the name to use for the User-Agent header. It can be specified in the ``name/version`` format, if
            applicable. The resulting header will be set to::

                pywmflib/{version} {name} +https://wikitech.wikimedia.org/wiki/Python/Wmflib root@wikimedia.org
        timeout (float, tuple): the default timeout to use in all requests within this session, in seconds. Any request
            can override it passing the ``timeout`` parameter explicitely. It can be either a single float or a tuple
            of two floats (connect, read), according to requests's documentation.
        tries (int): the total number of requests to perform before bailing out.
        backoff (float): the backoff factor to use, will generate a sleep between retries, in seconds, of::

            {backoff factor} * (2 ** ({number of total retries} - 1))

    Returns:
        requests.Session: the pre-configured session.

    """
    retry_strategy = Retry(total=tries, backoff_factor=backoff, status_forcelist=[429, 500, 502, 503, 504])
    adapter = TimeoutHTTPAdapter(timeout=timeout, max_retries=retry_strategy)
    session = Session()
    user_agent = f'pywmflib/{__version__} {name} +https://wikitech.wikimedia.org/wiki/Python/Wmflib'
    session.headers.update({'User-Agent': user_agent})
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
