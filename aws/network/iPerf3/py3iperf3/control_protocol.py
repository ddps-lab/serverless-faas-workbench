"""
Asyncio protocol for test control communication.
"""
import asyncio
import logging
import binascii

class ControlProtocol(asyncio.Protocol):
    """asyncio protocol for control connection"""

    def __init__(self, test=None):
        """Initialize the protocol"""
        self._test = test

        self._transport = None
        self._peer_data = None
        self._is_closed = False

        self._logger = logging.getLogger('py3iperf3')

    def connection_made(self, transport):
        """Connection made callback"""
        self._transport = transport
        self._peer_data = transport.get_extra_info('peername')
        self._logger.debug('Control connection made! Peer: %s', self._peer_data)
        self._test.server_connection_established(self)

    def connection_lost(self, exc):
        """Connection lost callback"""
        if not self._is_closed:
            self._logger.debug('Control connection lost!', exc_info=exc)
        self._test.stop()

    def data_received(self, data):
        """Data received callback"""
        self._logger.debug('Control connection data received. Len: %s bytes', len(data))
        self._logger.debug('RX data: %s', binascii.hexlify(data))
        self._test.handle_server_message(data)

    def send_data(self, data):
        """Send data over the control connection"""
        self._transport.write(data)

    def close_connection(self):
        """Close connection to the server"""
        self._logger.debug('Closing connection to the server')
        self._is_closed = True
        self._transport.close()