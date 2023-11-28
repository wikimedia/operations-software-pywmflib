"""Requests module."""
from typing import Any, Sequence, Tuple, Union

from requests import PreparedRequest, Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from wmflib import __version__


TimeoutType = Union[float, Tuple[float, float]]
"""Type alias for the requests timeout parameter."""
DEFAULT_TIMEOUT: TimeoutType = (3.0, 5.0)
""":py:class:`tuple`: the default timeout to use if none is passed, in seconds."""
DEFAULT_RETRY_STATUS_CODES: Tuple[int, ...] = (429, 500, 502, 503, 504)
""":py:class`tuple`: the default sequence of HTTP status codes that are retried if the method is one of
   :py:const:`DEFAULT_RETRY_METHODS`."""
DEFAULT_RETRY_METHODS: Tuple[str, ...] = ('DELETE', 'GET', 'HEAD', 'OPTIONS', 'PUT', 'TRACE')
""":py:class`tuple`: the default sequence of HTTP methods that are retried if the status code is one of
   :py:const:`DEFAULT_RETRY_STATUS_CODES`."""


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


def http_session(name: str, *, timeout: TimeoutType = DEFAULT_TIMEOUT, tries: int = 3, backoff: float = 1.0,
                 retry_codes: Sequence[int] = DEFAULT_RETRY_STATUS_CODES,
                 retry_methods: Sequence[str] = DEFAULT_RETRY_METHODS) -> Session:
    """Return a new requests Session with User-Agent, default timeout and retry logic on failure already setup.

    By default the returned session will retry any :py:const:`DEFAULT_RETRY_METHODS` request that returns one of
    the following HTTP status code (see :py:const:`DEFAULT_RETRY_STATUS_CODES`):

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

            session = http_session('AppName', timeout=10.0, tries=5, backoff=2.0, retry_codes=(429,))
            session = http_session('AppName', timeout=(3.0, 10.0), tries=5, backoff=2.0, retry_methods=('GET',))
            # Disable the retry logic, just set the User-Agent and default timeout
            session = http_session('AppName', tries=0)

    See Also:
        https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry
        https://requests.readthedocs.io/en/latest/user/advanced/#timeouts

    Arguments:
        name (str): the name to use for the User-Agent header. It can be specified in the ``name/version`` format, if
            applicable. The resulting header will be set to::

                pywmflib/{version} {name} +https://wikitech.wikimedia.org/wiki/Python/Wmflib root@wikimedia.org
        timeout (:py:data:`wmflib.requests.TimeoutType`): the default timeout to use in all requests within this
            session, in seconds. Any request can override it passing the ``timeout`` parameter explicitely. It can be
            either a single float or a tuple of two floats (connect, read), according to requests's documentation.
        tries (int): the total number of requests to perform before bailing out. If set to ``0`` the whole retry logic
            is not added to the session, making all the other parameters except the ``name`` one to be ignored. In this
            case only the User-Agent and default timeout are set.
        backoff (float): the backoff factor to use, will generate a sleep between retries, in seconds, of::

            {backoff factor} * (2 ** ({number of total retries} - 1))

        retry_codes (sequence): a sequence of integers with the list of HTTP status codes to retry instead of the
            default of :py:const:`DEFAULT_RETRY_STATUS_CODES`.
        retry_methods (sequence): a sequence of strings with the list of HTTP methods to retry intead of the default
            default of :py:const:`DEFAULT_RETRY_METHODS`.

    Returns:
        requests.Session: the pre-configured session.

    """
    # The method_whitelist parameter has been deprecated since urllib3 v1.26.0 and will be removed in v2.0.
    # It has been renamed to allowed_methods in v1.26.0. Keep backward compatibility.
    session = Session()
    user_agent = f'pywmflib/{__version__} {name} +https://wikitech.wikimedia.org/wiki/Python/Wmflib'
    session.headers.update({'User-Agent': user_agent})

    if tries > 0:
        methods_param_name = 'allowed_methods' if hasattr(Retry.DEFAULT, 'allowed_methods') else 'method_whitelist'
        # TODO: add type hint with Literal once Python 3.7 support is dropped and remove the type ignore on line 145
        params = {
            'total': tries,
            'backoff_factor': backoff,
            'status_forcelist': retry_codes,
            methods_param_name: retry_methods,
        }
        retry_strategy = Retry(**params)  # type: ignore[arg-type]
        adapter = TimeoutHTTPAdapter(timeout=timeout, max_retries=retry_strategy)
    else:
        adapter = TimeoutHTTPAdapter(timeout=timeout)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
