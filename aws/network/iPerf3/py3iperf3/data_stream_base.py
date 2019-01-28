"""
A base class for TCP and UDP test streams.
"""
import random
import logging
import time

from py3iperf3.error import IPerf3Exception

class BaseTestStream(object):
    """Class implementing common methods for TCP and UDP test streams"""

    def __init__(self, **kwargs):
        self._loop = kwargs.get('loop')
        self._test = kwargs.get('test')
        self._logger = logging.getLogger('py3iperf3')
        self._stream_id = kwargs.get('stream_id')

        self.done = False

        self._test_protocol = None
        self._sending_handle = None

        self._time_stream_start = None
        self._time_stream_stop = None

        self._block_size = self._test.block_size
        self._stop_on = self._test.test_type

        self._stat_objs = []
        self._bytes_tx_this_interval = 0
        self._bytes_rx_this_interval = 0
        self._blocks_tx_this_interval = 0
        self._pkt_tx_this_interval = 0
        self._pkt_rx_this_interval = 0

        self._data_source_sink = None # Either byte array or file handle

        # Will this stream send data?
        if ((self._test.role == 'c' and self._test.sender) or
            (self._test.role == 's' and not self._test.sender)):

            if self._test.file is None:
                self._data_source_sink = bytearray(
                    random.getrandbits(8) for _ in range(self._block_size))
            else:
                self._data_source_sink = open(
                    self._test.file, 'rb')
        else:
            # This stream will receive data
            if self._test.file is not None:
                self._data_source_sink = open(
                    self._test.file, 'rb+')

    @property
    def socket_id(self):
        """Get small int representing socket"""
        return self._test_protocol.socket_id

    def save_stats(self, t_start, t_end, t_sec):
        """Save interval stats to the stats object &
           return an opaque stats obj to the caller.
        """
        pass

    def print_last_stats_entry(self):
        """Print the last entry in the stats storage"""
        pass

    def print_sum_stats(self, stat_list):
        """Given a list of stats objects print a sum"""
        pass

    def create_connection(self):
        """Create a new connections"""
        pass

    def data_received(self, data, remote_addr=None):
        """Call-back: Data received on the test data connection"""
        self._bytes_rx_this_interval += len(data)

        if self._test.file:
            try:
                self._data_source_sink.write(data)
            except OSError as exc:
                logging.exception('Failed to write received data to file',
                                  exc_info=exc)
                raise IPerf3Exception('Failed to write RX data to file')

    def _try_sending(self):
        """
        Check the time/block/bytes gating and send if possible.
        """
        if self._stop_on == 't':
            # Time based test will be stopped by the test class
            self._send_block()
            self._sending_handle = self._loop.call_soon(self._try_sending)

        elif self._stop_on == 'b':
            # Check the remianing block count
            if self._test._blocks_remaining:
                self._test._blocks_remaining -= 1
                self._send_block()
                self._sending_handle = self._loop.call_soon(self._try_sending)

            else:
                # No more blocks to send. Inform test and do not reschedule sending
                self._sending_handle = None
                self.done = True
                self._test.sendable_data_depleted()

        elif self._stop_on == 's':
            # Check the remaining bytes count

            if self._test._bytes_remaining > self._block_size:
                # Send the whole block, reduce size as normal
                self._test._bytes_remaining -= self._block_size
                self._send_block()
                self._sending_handle = self._loop.call_soon(self._try_sending)

            elif self._test._bytes_remaining > 0:
                # Sent the whole block, reduce to 0
                self._test._bytes_remaining = 0
                self._send_block()
                self._sending_handle = None
                self.done = True
                self._test.sendable_data_depleted()

            else:
                self._sending_handle = None
                self.done = True
                self._test.sendable_data_depleted()

    def _get_block(self):
        """Get data block for sending"""

        # What is data_source_sink
        if self._test.file:
            bytes_data = self._data_source_sink.read(
                self._block_size)

            # Empty bytes() == file EOF
            if bytes_data is bytes():
                self.done = True
                self._test.sendable_data_depleted()

            return bytes_data
        else:
            # Random bytearray
            return self._data_source_sink

    def _send_block(self):
        """Send data over the test protocol"""

        data_block = self._get_block()

        # We might run out of memory in some cases
        try:
            self._test_protocol.send_data(data_block)
        except MemoryError as exc:
            # Program failed at memory alloc
            # Not a biggy, try later...
            self._logger.exception('[%s] Stream Out-of-Memory: ', self.socket_id, exc_info=exc)
            return

        self._blocks_tx_this_interval += 1
        self._bytes_tx_this_interval += len(data_block)

    def start_stream(self):
        """Start sending data"""

        self._time_stream_start = time.time()
        if self._sending_handle is None:
            self._sending_handle = self._loop.call_soon(self._try_sending)

    def stop_stream(self):
        """Stop sending data"""

        # One shot action
        if self.done:
            return

        self._logger.debug('Stop stream called')
        self._time_stream_stop = time.time()

        if self._sending_handle is not None:
            self._sending_handle.cancel()
            self._sending_handle = None

        # Close file handle if file is used
        if self._test.file:
            self._data_source_sink.close()

        self.done = True

    def set_proto(self, proto):
        """Set the protocol when working in server mode"""
        # Link us with proto
        self._test_protocol = proto
        # Link proto with us
        proto.set_owner(self, is_stream=True)

    def get_stats_header(self):
        """
        Get stats headers for each proto/direction case.
        """
        pass

    def get_final_stats(self):
        """
        Get the final stats object
        """

        stats_obj = {
            "id":self._stream_id,
            "bytes":sum([x['bytes'] for x in self._stat_objs]),
            "retransmits":-1,
            "jitter":0,
            "errors":0,
            "packets":0,
        }

        return stats_obj

    def get_interval_stats(self, t_start, t_end, t_sec):
        """
        Get stats for the given interval.
        N.B. Extending function should save object in stats array!
        N.B. Extending function should reset protocol specific counters!
        """

        # Account for test direction
        if self._test.sender:
            num_bytes = self._bytes_tx_this_interval
        else:
            num_bytes = self._bytes_rx_this_interval

        # Save stats object
        stats = {
            "socket":	        self._test_protocol.socket_id,
            "start":	        t_start,
            "end":	            t_end,
            "seconds":	        t_sec,
            "bytes":	        num_bytes,
            "bits_per_second":	int(num_bytes * 8 / t_sec),
            "omitted":	        False,
            "errors":           0,
        }

        # Reset the counters
        self._bytes_rx_this_interval = 0
        self._bytes_tx_this_interval = 0
        self._blocks_tx_this_interval = 0

        return stats