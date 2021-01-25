"""IRC utils module tests."""
import logging

from unittest import mock

from wmflib.irc import SALSocketHandler


GENERIC_LOG_RECORD = logging.LogRecord('module', logging.DEBUG, '/source/file.py', 1, 'message', [], None)


@mock.patch('socket.gethostname', return_value='current-hostname')
def test_irc_socket_handler_init(mocked_hostname):
    """An instance of SALSocketHandler should set the address for the socket and the user."""
    handler = SALSocketHandler('host', 123, 'user')
    assert handler.addr == ('host', 123)
    assert handler.username == 'user'
    assert handler.hostname == 'current-hostname'
    mocked_hostname.assert_called_once_with()


@mock.patch('wmflib.irc.socket')
def test_irc_socket_handler_emit_ok(mocked_socket):
    """Calling emit() on an SALSocketHandler instance should send the message to the socket."""
    handler = SALSocketHandler('host', 123, 'user')

    handler.emit(GENERIC_LOG_RECORD)

    mocked_socket.assert_has_calls([
        mock.call.socket().connect(('host', 123)), mock.call.socket().close()], any_order=True)


@mock.patch('wmflib.irc.socket')
def test_irc_socket_handler_emit_ko(mocked_socket):
    """If an error occur while calling emit() on an SALSocketHandler instance, it should call ."""
    handler = SALSocketHandler('host', 123, 'user')
    handler.handleError = mock.MagicMock()
    mocked_socket.socket.side_effect = OSError

    handler.emit(GENERIC_LOG_RECORD)

    assert mock.call.socket().connect(('host', 123)) not in mocked_socket.mock_calls
    assert mock.call.socket().close() not in mocked_socket.mock_calls
    handler.handleError.assert_called_once_with(GENERIC_LOG_RECORD)
