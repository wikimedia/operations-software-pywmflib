"""IRC module."""

import logging
import socket

from typing import Tuple


class SocketHandler(logging.Handler):
    """Log handler to communicate with logmsgbot.

    Sends log events to a tcpircbot server for relay to an IRC channel.
    The combination of hostname:port identifies a specific IRC channel,
    and for the moment only the #wikimedia-operations one is configured.
    Please also keep in mind that SRE allows only specific hostnames to
    send traffic to tcpircbot, so follow up with them in case you have
    doubts or special requests.
    For more info, please check the tcpircbot config in puppet.
    """

    prefix = '{s.username}@{s.hostname}'

    def __init__(self, host: str, port: int, username: str) -> None:
        """Initialize the IRC socket handler.

        Arguments:
            host (str): tcpircbot hostname.
            port (int): tcpircbot listening port.
            username (str): the user to refer in the IRC messages.

        """
        super().__init__()
        self.addr: Tuple[str, int] = (host, port)
        self.username = username
        self.level = logging.INFO
        self.hostname = socket.gethostname()

    def _send_message(self, message: str, record: logging.LogRecord) -> None:
        """Send a custom message string on a socket."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect(self.addr)
            sock.sendall(message.encode('utf-8'))
        except OSError:
            self.handleError(record)
        finally:
            if sock is not None:
                sock.close()

    def emit(self, record: logging.LogRecord) -> None:
        """According to Python logging.Handler interface.

        See https://docs.python.org/3/library/logging.html#handler-objects
        """
        message = self.prefix.format(s=self) + ' ' + record.getMessage()
        self._send_message(message, record)


class SALSocketHandler(SocketHandler):
    """Log handler to !log on a SAL."""

    # Stashbot expects !log messages relayed by logmsgbot to have the
    # format: "!log <nick> <msg>". The <nick> is parsed out and used as
    # the label of who actually made the SAL entry.
    prefix = '!log {s.username}@{s.hostname}'
