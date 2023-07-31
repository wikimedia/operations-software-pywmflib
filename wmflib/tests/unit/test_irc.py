"""IRC utils module tests."""
import logging
import socket

from unittest import mock

from wmflib.irc import SALSocketHandler, SocketHandler


GENERIC_LOG_RECORD = logging.LogRecord('module', logging.DEBUG, '/source/file.py', 1, 'message', [], None)


class TestIrc:
    """Test class for the irc module."""

    @mock.patch('wmflib.irc.socket.gethostname', return_value='current-hostname')
    def setup_method(self, _, mocked_hostname):
        """Initialize the test instance."""
        # pylint: disable=attribute-defined-outside-init
        self.mocked_hostname = mocked_hostname
        self.handler = SocketHandler('host', 123, 'user')
        self.sal_handler = SALSocketHandler('host', 123, 'user')

    def test_socket_handler_init(self):
        """An instance of SocketHandler should set the address for the socket and the user."""
        assert self.handler.addr == ('host', 123)
        assert self.handler.username == 'user'
        assert self.handler.hostname == 'current-hostname'
        assert self.mocked_hostname.call_count == 2

    def test_irc_socket_handler_init(self):
        """An instance of SALSocketHandler should set the address for the socket and the user."""
        assert self.sal_handler.addr == ('host', 123)
        assert self.sal_handler.username == 'user'
        assert self.sal_handler.hostname == 'current-hostname'
        assert self.mocked_hostname.call_count == 2

    @mock.patch('wmflib.irc.socket.socket')
    def test_socket_handler_emit_ok(self, mocked_socket):
        """Calling emit() on an SocketHandler instance should send the message to the socket."""
        self.handler.emit(GENERIC_LOG_RECORD)
        assert mock.call().connect(('host', 123)) in mocked_socket.mock_calls
        assert mock.call().sendall(b'user@current-hostname message') in mocked_socket.mock_calls

    @mock.patch('wmflib.irc.socket.socket')
    def test_irc_socket_handler_emit_ok(self, mocked_socket):
        """Calling emit() on an SALSocketHandler instance should send the message to the socket."""
        self.sal_handler.emit(GENERIC_LOG_RECORD)
        assert mock.call().connect(('host', 123)) in mocked_socket.mock_calls
        assert mock.call().sendall(b'!log user@current-hostname message') in mocked_socket.mock_calls

    @mock.patch('wmflib.irc.socket.socket')
    def test_socket_handler_emit_formatted_ok(self, mocked_socket):
        """Calling emit() on a SALSocketHandler instance should use the formatter when set."""
        self.sal_handler.setFormatter(logging.Formatter('Prefix - %(message)s'))
        self.sal_handler.emit(GENERIC_LOG_RECORD)
        assert mock.call().connect(('host', 123)) in mocked_socket.mock_calls
        assert mock.call().sendall(b'!log user@current-hostname Prefix - message') in mocked_socket.mock_calls

    @mock.patch('wmflib.irc.socket.socket')
    def test_irc_socket_handler_emit_ko(self, mocked_socket):
        """If an error occur while calling emit() on an SALSocketHandler instance, it should call handleError."""
        self.sal_handler.handleError = mock.MagicMock()
        mocked_socket.side_effect = OSError

        self.sal_handler.emit(GENERIC_LOG_RECORD)

        mocked_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        self.sal_handler.handleError.assert_called_once_with(GENERIC_LOG_RECORD)
