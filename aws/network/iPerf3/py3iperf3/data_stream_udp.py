"""
Test data stream over UDP.
"""
import struct
import time

from py3iperf3.data_stream_base import BaseTestStream
from py3iperf3.data_protocol_udp import UdpTestProtocol
from py3iperf3.utils import data_size_formatter

class TestStreamUdp(BaseTestStream):
    """
    UDP Test data stream.
    """

    def __init__(self, **kwargs):
        """Init the UDP stream"""

        # Init the stream
        super().__init__(**kwargs)

        # Set UDP related values
        self._pkt_cnt = 0
        self._pkt_cnt_64bit = self._test._parameters.udp64bitcounters
        self._err_count = 0
        self._ooo_count = 0

        self._jitter = 0
        self._prev_transit = 0

    def create_connection(self):
        """
        Create UDP datagram socket.
        """
        connect_coro = self._loop.create_datagram_endpoint(
            lambda: UdpTestProtocol(test_stream=self),
            remote_addr=(
                self._test.server_address,
                self._test.server_port))
        self._loop.create_task(connect_coro)

    def connection_established(self, test_protocol):
        """
        Callback on connection established.
        """
        self._test_protocol = test_protocol

        for _ in range(1):
            self._test_protocol.send_data(
                struct.pack('>I', 12345678))

        self._logger.info('UDP Test: initial data')

    def data_received(self, data, remote_addr=None):
        """Data received callback"""

        # Ignore '123456789'
        if len(data) == 4:
            return

        self._pkt_rx_this_interval += 1

        # Extract time and packet count
        if self._pkt_cnt_64bit:
            (time_sec, time_usec, pkt_num) = struct.unpack(
                '>IIQ', data[:16])
        else:
            (time_sec, time_usec, pkt_num) = struct.unpack(
                '>III', data[:12])

        # Handle Out-Of-Order packets
        # Algo is lifted from ESnet iPerf3 code
        if pkt_num >= self._pkt_cnt + 1:

            # count errors
            if pkt_num > self._pkt_cnt + 1:
                self._err_count += (pkt_num - 1) - self._pkt_cnt

            # Update largest seen
            self._pkt_cnt = pkt_num
        else:
            # We got missing packet
            if pkt_num < self._pkt_cnt:
                self._lost_in_period -= 1

            self._ooo_count += 1
            if self._err_count > 0:
                self._err_count -= 1

            self._logger.debug("Out-of-Order Packet: Incoming seq: %s but expected %s",
                               pkt_num, self._pkt_cnt)

        # Jitter calc
        transit = time.time() - time_sec - (time_usec / 1000000)
        d = transit - self._prev_transit
        if d < 0:
            d = -d

        self._prev_transit = transit
        self._jitter += (d - self._jitter) / 16.0

        # Handle received data as normal
        super().data_received(data, remote_addr)

    def _get_block(self):
        """Get block to send and make UDP changes"""

        block_bytes = super()._get_block()

        time_now = time.time()
        time_sec = int(time_now)
        time_usec = int((time_now % 1) * 1000000)

        # Handle 64-bit counters
        if self._pkt_cnt_64bit:
            udp_extras = struct.pack('>IIQ',
                                     time_sec,
                                     time_usec,
                                     self._pkt_cnt)
            block_bytes = udp_extras + block_bytes[16:]
        else:
            udp_extras = struct.pack('>III',
                                     time_sec,
                                     time_usec,
                                     self._pkt_cnt)
            block_bytes = udp_extras + block_bytes[12:]

        return block_bytes

    def _send_block(self):
        """Extend sending function with packets counting"""

        # Send the block
        super()._send_block()

        # Increase the counters
        self._pkt_tx_this_interval += 1
        self._pkt_cnt += 1

    def get_final_stats(self):
        """
        Get base stats object and update with extra data.
        """

        stats = super().get_final_stats()
        stats['packets'] = sum([x['packets'] for x in self._stat_objs])
        stats['errors'] = sum([x['errors'] for x in self._stat_objs])

        return stats

    def get_interval_stats(self, t_start, t_end, t_sec):
        """
        Get interval stats. Extend and reset packet counters.
        """

        stats = super().get_interval_stats(t_start, t_end, t_sec)
        if self._test.sender:
            stats['packets'] = self._pkt_tx_this_interval
        else:
            stats['packets'] = self._pkt_rx_this_interval
            stats['errors'] = self._err_count
            stats['jitter'] = self._jitter
         
        self._pkt_tx_this_interval = 0
        self._pkt_rx_this_interval = 0
        self._err_count = 0

        self._stat_objs.append(stats)

        return stats

    def print_last_stats_entry(self):
        """
        Print sum stats over all time intervals.
        """

        # Get reference to the last entry
        stats = self._stat_objs[-1]

        # Format strings
        size_str = data_size_formatter(int(stats['bytes'])*8, in_bytes=True)
        speed_str = data_size_formatter(int(stats['bits_per_second']))

        base_str = '[{}] {:.2f}-{:.2f} sec {} {}/sec'.format(
            stats['socket'],
            stats['start'],
            stats['end'],
            size_str,
            speed_str)

        # Sender / receiver specific
        if self._test.sender:
            stat_str = '{} {}'.format(base_str, stats['packets'])
        else:
            # TODO: Jitter et. al.
            stat_str = '{}  {:.4f} ms   {}/{}'.format(
                base_str, stats['jitter'] * 1000, stats['errors'], stats['packets'])

        # Print entry
        self._logger.info(stat_str)

    def get_stats_header(self):
        """
        Different headers based on direction.
        """
        if self._test.sender:
            return '[ ID] Interval      Transfer    Bandwidth      Total datagrams'
        else:
            return '[ ID] Interval      Transfer    Bandwidth         Jitter   Lost/Total datagrams'