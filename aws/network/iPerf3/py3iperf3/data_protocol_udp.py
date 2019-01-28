"""
Asyncio protocol for UDP tests
"""
import asyncio
import logging

class UdpTestProtocol(asyncio.DatagramProtocol):
    """UDP Protocol implementation"""

    def __init__(self, test_stream=None):
        self._transport = None
        self._stream = test_stream
        self._logger = logging.getLogger('py3iperf3')
        self._sock_id = None

    @property
    def socket_id(self):
        """Return socket id"""
        return self._sock_id

    def connection_made(self, transport):
        self._transport = transport
        peer_data = transport.get_extra_info('peername')
        self._logger.debug('UDP Test connection made! Peer: %s', peer_data)

        socket = transport.get_extra_info('socket')
        self._sock_id = socket.fileno()

        self._stream.connection_established(self)

    def datagram_received(self, data, addr):
        self._stream.data_received(data, addr)

    def send_data(self, data):
        """
        Write data to transport.
        """
        self._transport.sendto(data)