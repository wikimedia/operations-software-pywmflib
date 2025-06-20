"""Dnsdisc module tests."""

from datetime import timedelta
from unittest import mock

import pytest

from wmflib.decorators import RetryParams, get_backoff_sleep, retry
from wmflib.exceptions import WmflibError


class TestRetryParams:
    """Test class for the RetryParams dataclass."""

    def setup_method(self):
        """Initialize the test instance."""
        # pylint: disable=attribute-defined-outside-init
        self.base_params = {
            "tries": 3,
            "delay": timedelta(seconds=10),
            "backoff_mode": "constant",
            "exceptions": (WmflibError,),
            "failure_message": "failed",
        }

    def test_validate_ok(self):
        """It should validate the parameters if they are correct."""
        params = RetryParams(**self.base_params)
        params.validate()  # Will raise if invalid

    @pytest.mark.parametrize(
        "modified, expected",
        (
            ({"backoff_mode": "invalid"}, "Invalid backoff_mode: invalid"),
            (
                {"backoff_mode": "exponential", "delay": timedelta(seconds=0.5)},
                "Delay must be greater than 1 if backoff_mode is exponential",
            ),
            ({"tries": 0}, "Tries must be a positive integer, got 0"),
            ({"failure_message": ""}, "A failure_message must be set."),
        ),
    )
    def test_validate_invalid_params(self, modified, expected):
        """It should raise WmflibError if the parameters are invalid."""
        params = RetryParams(**{**self.base_params, **modified})
        with pytest.raises(WmflibError, match=expected):
            params.validate()


def _generate_mocked_function(calls):
    func = mock.Mock()
    func.side_effect = calls
    func.__qualname__ = "mocked.func"
    return func


@pytest.mark.parametrize(
    "calls, sleep_calls",
    (
        ([True], []),
        ([WmflibError("error1"), True], [3.0]),
        ([WmflibError("error1"), WmflibError("error2"), True], [3.0, 9.0]),
    ),
)
@mock.patch("wmflib.decorators.time.sleep", return_value=None)
def test_retry_pass_no_args(mocked_sleep, calls, sleep_calls):
    """Using @retry with no arguments should use the default values."""
    func = _generate_mocked_function(calls)
    ret = retry(func)()
    assert ret
    func.assert_has_calls([mock.call()] * len(calls))
    mocked_sleep.assert_has_calls([mock.call(i) for i in sleep_calls])


@pytest.mark.parametrize(
    "exc, calls, sleep_calls",
    (
        (WmflibError, [WmflibError("error")] * 3, [3.0, 9.0]),
        (Exception, [Exception("error")], []),
    ),
)
@mock.patch("wmflib.decorators.time.sleep", return_value=None)
def test_retry_fail_no_args(mocked_sleep, exc, calls, sleep_calls):
    """Using @retry with no arguments should raise the exception raised by the decorated function if not cathced."""
    func = _generate_mocked_function(calls)
    with pytest.raises(exc, match="error"):
        retry(func)()

    func.assert_has_calls([mock.call()] * len(calls))
    mocked_sleep.assert_has_calls([mock.call(i) for i in sleep_calls])


@pytest.mark.parametrize(
    "calls, sleep_calls, kwargs",
    (
        ([True], [], {"delay": timedelta(seconds=11), "tries": 1}),
        (
            [Exception("error1"), True],
            [5.55],
            {"delay": timedelta(seconds=5, milliseconds=550), "tries": 2, "exceptions": Exception},
        ),
        (
            [WmflibError("error1"), True],
            [8.88],
            {"backoff_mode": "exponential", "delay": timedelta(milliseconds=8880), "tries": 2},
        ),
        (
            [WmflibError("error1"), True],
            [0.90],
            {"backoff_mode": "power", "delay": timedelta(milliseconds=900), "tries": 2},
        ),
    ),
)
@mock.patch("wmflib.decorators.time.sleep", return_value=None)
def test_retry_pass_args(mocked_sleep, calls, sleep_calls, kwargs):
    """Using @retry with arguments should use the specified values."""
    func = _generate_mocked_function(calls)
    ret = retry(**kwargs)(func)()

    assert ret
    func.assert_has_calls([mock.call()] * len(calls))
    mocked_sleep.assert_has_calls([mock.call(i) for i in sleep_calls])


@pytest.mark.parametrize(
    "exc, kwargs",
    (
        (WmflibError, {}),
        (RuntimeError, {"exceptions": (KeyError, ValueError)}),
    ),
)
@mock.patch("wmflib.decorators.time.sleep", return_value=None)
def test_retry_fail_args(mocked_sleep, exc, kwargs):
    """Using @retry with arguments should raise the exception raised by the decorated function if not cathced."""
    func = _generate_mocked_function([exc("error")])
    kwargs["tries"] = 1
    with pytest.raises(exc, match="error"):
        retry(**kwargs)(func)()

    func.assert_called_once_with()
    assert not mocked_sleep.called


@pytest.mark.parametrize(
    "failure_message, expected_log",
    (
        (None, "Attempt to run 'unittest.mock.mocked.func' raised:"),
        ("custom failure message", "custom failure message"),
    ),
)
@mock.patch("wmflib.decorators.time.sleep", return_value=None)
def test_retry_failure_message(mocked_sleep, failure_message, expected_log, caplog):
    """Using @retry with a failure_message should log that message when an exception is caught."""
    func = _generate_mocked_function([WmflibError("error1"), True])
    ret = retry(failure_message=failure_message)(func)()  # pylint: disable=no-value-for-parameter

    assert ret
    assert expected_log in caplog.text
    assert "error1" in caplog.text
    assert mocked_sleep.call_count == 1


@mock.patch("wmflib.decorators.time.sleep", return_value=None)
def test_retry_fail_chained_exceptions(mocked_sleep, caplog):
    """When @retry catches a chained exception, it should log exception messages all the way down the chain."""

    def side_effect():
        try:
            raise WmflibError("error2") from WmflibError("error3")  # noqa: TRY301
        except WmflibError:
            raise WmflibError("error1")  # noqa: B904

    func = _generate_mocked_function(side_effect)
    with pytest.raises(WmflibError, match="error1"):
        retry(func)()

    assert "error1\nRaised while handling: error2\nCaused by: error3" in caplog.text
    assert mocked_sleep.call_count == 2


@mock.patch("wmflib.decorators.time.sleep", return_value=None)
def test_retry_dynamic_params_callback(mocked_sleep):
    """It should execute the given callback and use the new parameters."""

    def callback(params, _func, _args, _kwargs):
        """Alter the tries value."""
        params.tries = 2

    func = _generate_mocked_function([WmflibError("error1"), True])
    ret = retry(tries=1, dynamic_params_callbacks=(callback,))(func)()  # pylint: disable=no-value-for-parameter

    assert ret
    assert mocked_sleep.call_count == 1


@pytest.mark.parametrize(
    "mode, base, values",
    (
        ("constant", 0, (0,) * 5),
        ("constant", 0.5, (0.5,) * 5),
        ("constant", 3, (3,) * 5),
        ("linear", 0, (0,) * 5),
        ("linear", 0.5, (0.5, 1.0, 1.5, 2.0, 2.5)),
        ("linear", 3, (3, 6, 9, 12, 15)),
        ("power", 0, (0,) * 5),
        ("power", 0.5, (0.5, 1, 2, 4, 8)),
        ("power", 3, (3, 6, 12, 24, 48)),
        ("exponential", 1, (1,) * 5),
        ("exponential", 1.5, (1.5, 2.25, 3.375, 5.0625, 7.59375)),
        ("exponential", 3, (3, 9, 27, 81, 243)),
    ),
)
def test_get_backoff_sleep(mode, base, values):
    """Calling get_backoff_sleep() should return the proper backoff based on the arguments."""
    for i, val in enumerate(values, start=1):
        assert get_backoff_sleep(mode, base, i) == pytest.approx(val)


def test_get_backoff_sleep_raise():
    """Calling get_backoff_sleep() with an invalid backoff_mode should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid backoff_mode: invalid"):
        get_backoff_sleep("invalid", 1, 5)
