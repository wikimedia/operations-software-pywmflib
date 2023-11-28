"""Decorators module."""
import logging
import time

from dataclasses import dataclass
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, cast, Dict, Optional, Tuple, Type, Union

from wmflib.exceptions import WmflibError


logger = logging.getLogger(__name__)


# TODO: use TypedDict once Python 3.7 support is removed
@dataclass
class RetryParams:
    """Retry decorator parameters class.

    This class represents the parameters that the :py:func:`wmflib.decorators.retry` decorator accepts and allow
    to validate them.

    It is also used for the `dynamic_params_callbacks` parameter of the same retry decorator to allow the callback to
    safely modify the decorator's parameters at runtime.
    """

    tries: int
    delay: timedelta
    backoff_mode: str
    exceptions: Tuple[Type[Exception], ...]
    failure_message: str

    def validate(self) -> None:
        """Validate the consistency of the current values of the instance properties.

        Raises:
            wmflib.exceptions.WmflibError: if any field has an invalid value.

        """
        if self.backoff_mode not in ('constant', 'linear', 'power', 'exponential'):
            raise WmflibError(f'Invalid backoff_mode: {self.backoff_mode}')

        if self.backoff_mode == 'exponential' and self.delay.total_seconds() < 1:
            raise WmflibError(f'Delay must be greater than 1 if backoff_mode is exponential, got {self.delay}')

        if self.tries < 1:
            raise WmflibError(f'Tries must be a positive integer, got {self.tries}')

        if not self.failure_message:
            raise WmflibError('A failure_message must be set.')


def ensure_wrap(func: Callable) -> Callable:
    """Decorator to wrap other decorators to allow to call them both with and without arguments.

    Arguments:
        func: the decorated function, it must be a decorator. A decorator that accepts only one positional argument
            that is also a callable is not supported.

    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Callable:
        """Decorator wrapper."""
        if len(args) == 1 and not kwargs and callable(args[0]):  # Called without arguments
            return func(args[0])

        return lambda real_func: func(real_func, *args, **kwargs)  # Called with arguments

    return wrapper


@ensure_wrap
def retry(
    func: Callable,
    *,
    tries: int = 3,
    delay: timedelta = timedelta(seconds=3),
    backoff_mode: str = 'exponential',
    exceptions: Tuple[Type[Exception], ...] = (WmflibError,),
    failure_message: Optional[str] = None,
    dynamic_params_callbacks: Tuple[Callable[[RetryParams, Callable, Tuple, Dict[str, Any]], None], ...] = (),
) -> Callable:
    """Decorator to retry a function or method if it raises certain exceptions with customizable backoff.

    Note:
        The decorated function or method must be idempotent to avoid unwanted side effects.
        It can be called with or without arguments, in the latter case all the default values will be used.

    Examples:
        Define a function that polls for the existence of a file, retrying with the default parameters::

            >>> from pathlib import Path
            >>> from wmflib.decorators import retry
            >>> from wmflib.exceptions import WmflibError
            >>> @retry
            ... def poll_file(path: Path):
            ...     if not path.exists():
            ...         raise WmflibError(f'File {path} not found')
            ...
            >>> poll_file(Path('/tmp'))
            >>> poll_file(Path('/tmp/nonexistent'))
            [1/3, retrying in 3.00s] Attempt to run '__main__.poll_file' raised: File /tmp/nonexistent not found
            [2/3, retrying in 9.00s] Attempt to run '__main__.poll_file' raised: File /tmp/nonexistent not found
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
              File "/usr/lib/python3/dist-packages/wmflib/decorators.py", line 160, in wrapper
                return func(*args, **kwargs)
              File "<stdin>", line 4, in poll_file
            wmflib.exceptions.WmflibError: File /tmp/nonexistent not found
            >>>

        Same example, but customizing the decorator parameters::

            >>> from datetime import timedelta
            >>> from pathlib import Path
            >>> from wmflib.decorators import retry
            >>> @retry(tries=5, delay=timedelta(seconds=30), backoff_mode='constant', failure_message='File not found',
            ...        exceptions=(RuntimeError,))
            ... def poll_file(path: Path):
            ...     if not path.exists():
            ...         raise RuntimeError(path)
            ...
            [1/5, retrying in 30.00s] File not found: /tmp/nonexistent
            [2/5, retrying in 30.00s] File not found: /tmp/nonexistent
            [3/5, retrying in 30.00s] File not found: /tmp/nonexistent
            [4/5, retrying in 30.00s] File not found: /tmp/nonexistent
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
              File "/usr/lib/python3/dist-packages/wmflib/decorators.py", line 160, in wrapper
                return func(*args, **kwargs)
              File "<stdin>", line 5, in poll_file
            RuntimeError: /tmp/nonexistent

    Arguments:
        func (function, method): the decorated function.
        tries (int, optional): the number of times to try calling the decorated function or method before giving up.
            Must be a positive integer.
        delay (datetime.timedelta, optional): the initial delay in seconds for the first retry, used also as the base
            for the backoff algorithm.
        backoff_mode (str, optional): the backoff mode to use for the delay, available values are shown below. All the
            examples are made with ``tries=5`` and ``delay=3``:

              * **constant**

                .. code-block:: text

                  Nth delay   = delay
                  Total delay = delay * tries
                  Example:      3s, 3s,  3s,  3s,   3s => 15s max possible delay

              * **linear**

                .. code-block:: text

                  Nth delay   = (delay * N) with N in [1, tries]
                  Total delay = 0.5 * tries * (delay + (delay * tries))
                  Example:      3s, 6s,  9s, 12s,  15s => 45s max possible delay

              * **power**

                .. code-block:: text

                  Nth delay   = (delay * 2^N) with N in [0, tries - 1]
                  Total delay = delay * (2**tries - 1)
                  Example:      3s, 6s, 12s, 24s,  48s => 93s max possible delay

              * **exponential**

                .. code-block:: text

                  Nth delay   = (delay^N) with N in [1, tries], delay must be > 1
                  Total delay = (delay * (delay**tries - 1)) / (delay - 1)
                  Example:      3s, 9s, 27s, 81s, 243s => 363s max possible delay

        exceptions (type, tuple, optional): the decorated function call will be retried if it fails until it succeeds
            or `tries` attempts are reached. A retryable failure is defined as raising any of the exceptions listed.
        failure_message (str, optional): the message to log each time there's a retryable failure. Retry information
            and exception message are also included. Default: "Attempt to run '<fully qualified function>' raised"
        dynamic_params_callbacks (tuple): a tuple of callbacks that will be called at runtime to allow to modify the
            decorator's parameters. Each callable must adhere to the following interface::

                def adjust_some_parameter(retry_params: RetryParams, func: Callable, args: Tuple, kwargs: Dict) -> None
                    # Modify the retry_params parameter possibly using the decorated function object or its parameters
                    # that are passed as tuple for the positional arguments and a dictionary for the keyword arguments

            This is a practical example that defines a callback that doubles the delay parameter of the ``@retry``
            decorator if the decorated function/method has a 'slow' keyword argument that is to True::

                def double_delay(retry_params, func, args, kwargs):
                    if kwargs.get('slow', False):
                        retry_params.delay = retry_params.delay * 2

                @retry(delay=timedelta(seconds=10), dynamic_params_callbacks=(double_delay,))
                def do_something(slow=False):
                    # This method will be retried using 10 seconds as delay parameter in the @retry decorator, but
                    # if the 'slow' parameter is set to True it will use a delay of 20 seconds instead.
                    # Do something here.

            **While the callbacks will have access to the parameters passed to the decorated function, they should be
            treated as read-only variables.**

    Returns:
        function: the decorated function.

    """
    if not failure_message:
        failure_message = f"Attempt to run '{func.__module__}.{func.__qualname__}' raised"

    static_params: Dict[str, Any] = {
        'tries': tries,
        'delay': delay,
        'backoff_mode': backoff_mode,
        'exceptions': exceptions,
        'failure_message': failure_message,
    }

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Decorated function."""
        params = RetryParams(**static_params)
        for dynamic_params_callback in dynamic_params_callbacks:
            dynamic_params_callback(params, func, args, kwargs)

        params.validate()
        attempt = 0
        while attempt < params.tries - 1:
            attempt += 1
            try:
                # Call the decorated function or method
                return func(*args, **kwargs)
            except exceptions as e:
                sleep = get_backoff_sleep(params.backoff_mode, params.delay.total_seconds(), attempt)
                logger.warning("[%d/%d, retrying in %.2fs] %s: %s",
                               attempt, params.tries, sleep, params.failure_message, _exception_message(e))
                time.sleep(sleep)

        return func(*args, **kwargs)

    return wrapper


def _exception_message(exception: BaseException) -> str:
    """Joins the message of the given exception with those of any chained exceptions.

    Arguments:
        exception (BaseException): The most-recently raised exception.

    Returns:
        str: The joined message, formatted suitably for logging.

    """
    message_parts = [str(exception)]
    while exception.__cause__ is not None or exception.__context__ is not None:
        # __cause__ and __context__ shouldn't both be set, but we use the same logic here as the built-in
        # exception handler, giving __cause__ priority, as described in PEP 3134. We list messages in
        # reverse order from the built-in handler (i.e. newest exception first) since we aren't following a
        # traceback.
        if exception.__cause__ is not None:
            message_parts.append(f'Caused by: {exception.__cause__}')
            exception = exception.__cause__
        else:  # e.__context__ is not None, due to the while condition.
            message_parts.append(f'Raised while handling: {exception.__context__}')
            exception = cast(BaseException, exception.__context__)  # Casting away the Optional.
    return '\n'.join(message_parts)


def get_backoff_sleep(backoff_mode: str, base: Union[int, float], index: int) -> Union[int, float]:
    """Calculate the amount of sleep for this attempt.

    Arguments:
        backoff_mode (str): the backoff mode to use for the delay, see the documentation for retry().
        base (int, float): the base for the backoff algorithm.
        index (int): the index to calculate the Nth sleep time for the backoff.

    Return:
        int, float: the amount of sleep to perform for the backoff.

    """
    if backoff_mode == 'constant':
        sleep = base
    elif backoff_mode == 'linear':
        sleep = base * index
    elif backoff_mode == 'power':
        sleep = base * 2 ** (index - 1)
    elif backoff_mode == 'exponential':
        sleep = base ** index
    else:
        raise ValueError(f'Invalid backoff_mode: {backoff_mode}')

    return sleep
