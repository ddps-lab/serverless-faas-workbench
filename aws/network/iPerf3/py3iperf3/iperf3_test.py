"""
A class representing a single iPerf3 test on both client and the server.
"""
import logging
import socket
import struct
import json
import time

from py3iperf3.control_protocol import ControlProtocol
from py3iperf3.utils import make_cookie, data_size_formatter
from py3iperf3.iperf3_api import Iperf3State, Iperf3TestProto
from py3iperf3.iperf3_api import DEFAULT_BLOCK_TCP, DEFAULT_BLOCK_UDP
from py3iperf3.data_stream_tcp import TestStreamTcp
from py3iperf3.data_stream_udp import TestStreamUdp
from py3iperf3.error import IPerf3Exception
from py3iperf3.settings import Iperf3TestSettings

class Iperf3Test(object):
    """description of class"""

    def __init__(self, master, loop, test_parameters):
        """ """
        self._master = master   # Ref to Client or Server
        self._loop = loop
        self._parameters = Iperf3TestSettings()
        self._logger = logging.getLogger('py3iperf3')
        self._disposed = False

        self._streams = []
        self._interval_stats = []
        self._next_stream_id = 1

        # Event handles
        self._hdl_stop_test = None
        self._hdl_omitting = None
        self._hdl_stats = None

        self._role = 'c'                # Default role is 'c'-lient, other 's'-server
        self._cookie = None
        self._control_protocol = None
        self._state = None
        self._remote_results = None

        self._test_stopper = 't'        # 't' - time; 'b' - blocks; 's' - data size
        self._blocks_remaining = None
        self._bytes_remaining = None
        self._depleted_called = False

        self._last_stat_collect_time = None
        self._stream_start_time = None
        self._stream_stop_time = None

        # Length prefixed strings reception
        self._string_drain = False
        self._string_length = None
        self._string_buffer = bytearray()

        # Overwrite defaults with given params
        self._set_test_parameters(test_parameters)

    @property
    def next_stream_id(self):
        """Get next stream id"""
        if self._next_stream_id == 2:
            self._next_stream_id += 1

        temp = self._next_stream_id
        self._next_stream_id += 1

        return temp

    @property
    def role(self):
        """Get test role"""
        return self._role

    @property
    def sender(self):
        """
        In client role sender is us, unless reverse.
        """
        if self._role == 'c':
            return not self._parameters.reverse

        return self._parameters.reverse

    @property
    def remote_results(self):
        """Get results received from remote peer"""
        return self._remote_results

    @property
    def cookie(self):
        if self._cookie is None:
            self._cookie = make_cookie()

        return self._cookie

    @property
    def server_address(self):
        return self._parameters.server_address

    @property
    def server_port(self):
        return self._parameters.server_port

    @property
    def data_protocol(self):
        return self._parameters.test_protocol

    @property
    def block_size(self):
        return self._parameters.block_size

    @property
    def test_type(self):
        # What stops the test (time/tx blocks/tx data)
        return self._test_stopper

    @property
    def file(self):
        """Get the read/write file"""
        return self._parameters.file

    @property
    def no_delay(self):
        """Get NoDelay property"""
        return self._parameters.no_delay

    @property
    def window(self):
        """Get Window property"""
        return self._parameters.window

    @property
    def ip_version(self):
        """Get IP version"""
        return self._parameters.ip_version

    def run(self):
        """Start the test"""
        self._connect_to_server()

    def stop(self):
        """Stop the test"""

        # One shot only
        if self._disposed:
            return

        self._client_cleanup()
        self._disposed = True

    def set_control_connection(self, control_protocol, cookie):
        """Link a test with a control protocol in the server"""

        # Update the state of the test
        self._control_protocol = control_protocol
        control_protocol.set_owner(self)
        self._cookie = cookie
        self._role = 's'

        # Initiate parameters exchange
        self._set_and_send_state(Iperf3State.PARAM_EXCHANGE)
        self._string_drain = True

    def new_data_connection(self, proto):
        """Link this test with a new data connection"""

        if self._parameters.test_protocol == Iperf3TestProto.TCP:
            stream = TestStreamTcp(loop=self._loop, test=self, stream_id=self.next_stream_id)
            stream.set_proto(proto)
        else:
            pass

        self._streams.append(stream)
        if len(self._streams) == self._parameters.parallel:
            self._set_and_send_state(Iperf3State.TEST_START)

            self._stream_start_time = time.time()
            self._hdl_stats = self._loop.call_later(
                self._parameters.report_interval,
                self._collect_print_stats)

            self._set_and_send_state(Iperf3State.TEST_RUNNING)

    def _parse_received_params(self, received_string):
        """Parse parameters received from the client"""

        test_params = json.loads(received_string)
        print(received_string)

        # TODO: Apply received parameters
        for key, value in test_params.items():
            if key == 'parallel':
                self._parameters.parallel = value
            if key == 'reverse':
                self._parameters.reverse = True

        # Request streams
        self._set_and_send_state(Iperf3State.CREATE_STREAMS)

    def server_connection_established(self, control_protocol):
        """Callback on established server connection"""
        self._control_protocol = control_protocol

        # Make and send cookie
        self._control_protocol.send_data(
            self.cookie.encode('ascii'))

    def control_data_received(self, _, message):
        """Handle data received from the client"""
        
        # Special handling of length prefixed strings
        if self._string_drain:
            self._drain_to_string(message)
            return

        if len(message) == 1:
            op_codes = struct.unpack('>B', message)
            self._logger.debug("codes: %s", op_codes)
        elif len(message) == 2:
            op_codes = struct.unpack('>BB', message)
            self._logger.debug("codes: %s", op_codes)
        else:
            raise IPerf3Exception('Whoopsy Daisy too many op-codes from the server!')

        for op_code in op_codes:
            self._logger.debug('Op code: %s', op_code)
            state = Iperf3State(op_code)
            self._logger.debug('Received %s state from the client', state)
            self._state = state

            if self._state == Iperf3State.TEST_END:
                # Client done sending
                self._stream_stop_time = time.time()
                if self._hdl_stats is not None:
                    self._hdl_stats.cancel()
                    self._hdl_stats = None
                self._set_and_send_state(Iperf3State.EXCHANGE_RESULTS)
                self._string_drain = True

            elif self._state == Iperf3State.DISPLAY_RESULTS:
                self.display_results()

    def handle_server_message(self, message):
        """Handle message received from the control socket"""

        # Special handling of length prefixed strings
        if self._string_drain:
            self._drain_to_string(message)
            return

        if len(message) == 1:
            op_codes = struct.unpack('>B', message)
            self._logger.debug("codes: %s", op_codes)
        elif len(message) == 2:
            op_codes = struct.unpack('>BB', message)
            self._logger.debug("codes: %s", op_codes)
        else:
            raise IPerf3Exception('Whoopsy Daisy too many op-codes from the server!')

        for op_code in op_codes:
            self._logger.debug('Op code: %s', op_code)
            state = Iperf3State(op_code)
            self._logger.debug('Received %s state from server', state)
            self._state = state

            if self._state == Iperf3State.PARAM_EXCHANGE:
                # Exchange params
                self._exchange_parameters()

            elif self._state == Iperf3State.CREATE_STREAMS:
                # Create required streams
                self._create_streams()
            elif self._state == Iperf3State.TEST_START:
                if not self._parameters.reverse:
                    for stream in self._streams:
                        stream.start_stream()

                self._stream_start_time = time.time()

                if self._test_stopper == 't':
                    self._hdl_stop_test = self._loop.call_later(
                        self._parameters.test_duration,
                        self._stop_all_streams)

                self._hdl_stats = self._loop.call_later(
                    self._parameters.report_interval,
                    self._collect_print_stats)

            elif self._state == Iperf3State.TEST_RUNNING:
                header = self._streams[0].get_stats_header()
                self._logger.info(header)
            elif self._state == Iperf3State.EXCHANGE_RESULTS:
                self._send_results()
                self._string_drain = True # Expect string reply from the server

            elif self._state == Iperf3State.DISPLAY_RESULTS:
                self.display_results()
                self._client_cleanup()
                self._disposed = True
            elif self._state == Iperf3State.IPERF_DONE:
                pass
            elif self._state == Iperf3State.SERVER_TERMINATE:
                pass
            elif self._state == Iperf3State.ACCESS_DENIED:
                raise IPerf3Exception('Access Denied')
            elif self._state == Iperf3State.SERVER_ERROR:
                pass
            else:
                self._logger.debug('Unknown state ID received')

    def display_results(self):
        """
        Display results after the test
        TODO: Final/Sum results should be generated by each stream
        """
        self._logger.debug('Received results: %s', self.remote_results)
        self._logger.info('- - - - - - - - - - - - - - - - - - - - - - - - -')
        self._logger.info('Test Complete. Summary Results:')
        header = self._streams[0].get_stats_header()
        self._logger.info(header)

        """
        File Write
        """
        log = open("/tmp/log.out", "a")

        local_stats_list = []
        remote_stats_list = []

        # Get starts from us and remote
        for stream in self._streams:
            our_stats = stream.get_final_stats()
            remote_stats = None

            # Filter required stream
            for stat_ob in self.remote_results['streams']:
                if stat_ob['id'] == our_stats['id']:
                    remote_stats = stat_ob

            # TODO: Use each streams time length
            test_len = self._stream_stop_time - self._stream_start_time

            # Format our numbers
            our_data_str = data_size_formatter(
                our_stats['bytes'], None, None, 'm')
            our_speed_str = data_size_formatter(
                int(our_stats['bytes'] * 8 / test_len), None, None, 'm')

            # Format remote numbers
            remote_data_str = data_size_formatter(
                remote_stats['bytes'], None, None, 'm')
            remote_speed_str = data_size_formatter(
                int(remote_stats['bytes'] * 8 / test_len), None, None, 'm')

            # Print entry
            self._logger.info('[{}] 0.00-{:.2f} sec {} {}/sec   local'.format(
                stream.socket_id, test_len, our_data_str, our_speed_str))
            log.write('Lambda:{}:{}/sec\n'.format(
                our_data_str, our_speed_str))
            self._logger.info('[{}] 0.00-{:.2f} sec {} {}/sec   remote'.format(
                stream.socket_id, test_len, remote_data_str, remote_speed_str))
            log.write('Server:{}:{}/sec\n'.format(
                remote_data_str, remote_speed_str))
            # Add for later usage (if num stream > 1)
            local_stats_list.append(our_stats)
            remote_stats_list.append(remote_stats)

        # Calculate sum stats if required
        if len(self._streams) > 1:
            test_len = self._stream_stop_time - self._stream_start_time
            sum_local = sum([x['bytes'] for x in local_stats_list])
            sum_remote = sum([x['bytes'] for x in remote_stats_list])

            # Format our numbers
            our_data_str = data_size_formatter(
                sum_local, None, None, 'm')
            our_speed_str = data_size_formatter(
                int(sum_local * 8 / test_len), None, None, 'm')

            # Format remote numbers
            remote_data_str = data_size_formatter(
                sum_remote, None, None, 'm')
            remote_speed_str = data_size_formatter(
                int(sum_remote * 8 / test_len), None, None, 'm')

            # Print entry
            self._logger.info('[SUM] 0.00-{:.2f} sec {} {}/sec   local'.format(
                test_len, our_data_str, our_speed_str))
            self._logger.info('[SUM] 0.00-{:.2f} sec {} {}/sec   remote'.format(
                test_len, remote_data_str, remote_speed_str))
        log.close()

    def sendable_data_depleted(self):
        """Called when blockcount is set and no more blocks remain"""
        # This could be implemented via the get/set property

        if self._depleted_called:
            return

        self._depleted_called = True
        self._stop_all_streams()

    def _collect_print_stats(self):
        """Collect and print periodic statistics"""

        all_stream_stats = []
        t_now = time.time()

        if self._last_stat_collect_time is None:
            scratch_start = 0
        else:
            scratch_start = self._last_stat_collect_time - self._stream_start_time

        scratch_end = t_now - self._stream_start_time
        scratch_seconds = t_now - self._stream_start_time - scratch_start

        self._last_stat_collect_time = t_now

        # Collect and print individual stats
        # Check if we need sum stats
        if len(self._streams) > 1:
            all_stats = []
            for stream in self._streams:
                all_stats.append(stream.get_interval_stats(scratch_start, scratch_end, scratch_seconds))
                stream.print_last_stats_entry()
            self._streams[0].print_sum_stats(all_stats)
        else:
            self._streams[0].get_interval_stats(scratch_start, scratch_end, scratch_seconds)
            self._streams[0].print_last_stats_entry()

        self._hdl_stats = self._loop.call_later(
            self._parameters.report_interval,
            self._collect_print_stats)

    def _client_cleanup(self):

        # close all streams
        for stream in self._streams:
            stream.stop_stream()

        # Graceful bye-bye to the server
        self._set_and_send_state(Iperf3State.IPERF_DONE)

        # close control socket
        self._control_protocol.close_connection()

        # Inform master that we are done!
        self._master.test_done(self)

    def _drain_to_string(self, message):

        if self._string_length is None:
            # Drain to buffer until we have at least 4 bytes
            self._string_buffer.extend(message)

            # Return if still not enough data:
            if len(self._string_buffer) < 4:
                return
            else:
                # Parse string length
                self._string_length = struct.unpack('!I', self._string_buffer[:4])[0]
                self._string_buffer = self._string_buffer[4:]
        else:
            self._string_buffer.extend(message)

        # Keep draining until we have enough data
        if len(self._string_buffer) < self._string_length:
            return

        # Decode the string
        string_bytes = self._string_buffer[:self._string_length]
        received_string = string_bytes.decode('ascii')

        # Cleanup
        scratch = self._string_buffer[self._string_length:]
        self._string_length = None
        self._string_buffer = bytearray()
        self._string_drain = False

        self._logger.debug('String draining done!')

        if self.role == 'c':
            self._save_received_results(received_string)
        else:
            # This is server
            if self._state == Iperf3State.PARAM_EXCHANGE:
                self._parse_received_params(received_string)
            elif self._state == Iperf3State.EXCHANGE_RESULTS:
                # Send our results
                self._send_results()
                # Collect client's results
                self._save_received_results(received_string)
                # Transition to show results state
                self._set_and_send_state(Iperf3State.DISPLAY_RESULTS)
                # TODO: cleanup

        # If anything extra is left - process as normal
        if scratch:
            self.handle_server_message(scratch)

    def _save_received_results(self, result_string):
        """Save results string from the server"""

        result_obj = json.loads(result_string)
        self._remote_results = result_obj

    def _send_results(self):
        """Send test results to remote peer"""

        results_obj = {}

        results_obj["cpu_util_total"] = 0
        results_obj["cpu_util_user"] = 0
        results_obj["cpu_util_system"] = 0

        results_obj["sender_has_retransmits"] = -1
        results_obj["congestion_used"] = "Unknown"
        results_obj["streams"] = []

        for stream in self._streams:
            results_obj["streams"].append(
                stream.get_final_stats())

        json_string = json.dumps(results_obj)
        self._logger.debug('Client stats JSON string: %s', json_string)

        len_bytes = struct.pack('!i', len(json_string))
        self._control_protocol.send_data(len_bytes)
        self._control_protocol.send_data(json_string.encode('ascii'))

    def _stop_all_streams(self):

        self._logger.debug('Stopping all streams!')

        self._stream_stop_time = time.time()

        # Stop streams
        for stream in self._streams:
            stream.stop_stream()

        # Stop proress reporting
        if self._hdl_stats is not None:
            self._hdl_stats.cancel()
            self._hdl_stats = None

        self._set_and_send_state(Iperf3State.TEST_END)

    def _set_and_send_state(self, state):
        """Set test state and send op_code"""

        self._logger.debug('Set and send state: %s', state)

        self._state = state
        self._control_protocol.send_data(
            struct.pack('!c', bytes([state.value])))

    def _set_test_parameters(self, test_parameters):
        """Set test parameters"""

        for attr, value in test_parameters.items():
            # Set default if Not given
            if value is not None:
                setattr(self._parameters, attr, value)
                
        self._parameters.server_port = test_parameters['server-port']
        
        if self._parameters.block_size is None:
            if self._parameters.test_protocol == Iperf3TestProto.TCP:
                self._parameters.block_size = DEFAULT_BLOCK_TCP
            elif self._parameters.test_protocol == Iperf3TestProto.UDP:
                self._parameters.block_size = DEFAULT_BLOCK_UDP
            else:
                self._parameters.block_size = 1000

        # Remaining time counter
        if self._parameters.test_duration:
            self._test_stopper = 't'

        # Remaining blocks counter
        if self._parameters.blockcount:
            self._blocks_remaining = self._parameters.blockcount
            self._test_stopper = 'b'

        # Remaining bytes counter
        if self._parameters.bytes:
            self._bytes_remaining = self._parameters.bytes
            self._test_stopper = 's'

    def _create_streams(self):
        """Create test streams"""

        try:
            for _ in range(self._parameters.parallel):
                if self.data_protocol == Iperf3TestProto.TCP:
                    test_stream = TestStreamTcp(loop=self._loop, test=self, stream_id=self._next_stream_id)
                elif self.data_protocol == Iperf3TestProto.UDP:
                    test_stream = TestStreamUdp(loop=self._loop, test=self, stream_id=self._next_stream_id)
                else:
                    raise IPerf3Exception('The required data protocol is not implemented (yet)')

                # Skip 2 in streams numbering
                if self._next_stream_id == 1:
                    self._next_stream_id = 3
                else:
                    self._next_stream_id += 1

                test_stream.create_connection()
                self._streams.append(test_stream)
        except OSError as exc:
            self._logger.exception('Failed creating stream!', exc_info=exc)
            raise IPerf3Exception('Failed to create test stream!')

    def _exchange_parameters(self):
        """Send test parameters to the server"""

        param_obj = {}

        if self.data_protocol == Iperf3TestProto.TCP:
            param_obj['tcp'] = True
        elif self.data_protocol == Iperf3TestProto.UDP:
            param_obj['udp'] = True
        param_obj['omit'] = 0
        param_obj['time'] = self._parameters.test_duration
        if self._parameters.bytes:
            param_obj['num'] = self._parameters.bytes
        if self._parameters.blockcount:
            param_obj['blockcount'] = self._parameters.blockcount
        #param_obj['MSS'] = 1400
        if self._parameters.no_delay:
            param_obj['nodelay'] = True
        param_obj['parallel'] = self._parameters.parallel
        if self._parameters.reverse:
            param_obj['reverse'] = True
        if self._parameters.window:
            param_obj['window'] = self._parameters.window
        param_obj['len'] = self._parameters.block_size
        #param_obj['bandwidth'] = 1
        #param_obj['fqrate'] = 1
        #param_obj['pacing_timer'] = 1
        #param_obj['burst'] = 1
        #param_obj['TOS'] = 1
        #param_obj['flowlabel'] = 1
        if self._parameters.title:
            param_obj['title'] = self._parameters.title
        #param_obj['congestion'] = ''
        #param_obj['congestion_used'] = ''
        if self._parameters.get_server_output:
            param_obj['get_server_output'] = 1
        if self._parameters.udp64bitcounters:
            param_obj['udp_counters_64bit'] = 1
        #param_obj['authtoken'] = ''
        param_obj['client_version'] = 'py3iPerf3_v0.9'

        json_str = json.dumps(param_obj)
        self._logger.debug('Settings JSON (%s): %s',
                           len(json_str), json_str)

        len_bytes = struct.pack('!i', len(json_str))
        self._control_protocol.send_data(len_bytes)
        str_bytes = json_str.encode('ascii')
        self._control_protocol.send_data(str_bytes)

    def _connect_to_server(self):
        """Make a control connection to the server"""
        self._logger.info('Connecting to server %s:%s',
                          self._parameters.server_address,
                          self._parameters.server_port)
        
        # Connect to
        connect_params = {
            'host' : self._parameters.server_address,
            'port' : self._parameters.server_port
        }

        # Bind on
        if self._parameters.client_address or self._parameters.client_port:

            if self._parameters.client_address is None:
                if (self._parameters.ip_version and
                    self._parameters.ip_version == 6):

                    local_addr = '::'
                else:
                    local_addr = '0.0.0.0'

            else:
                local_addr = self._parameters.client_address

            if self._parameters.client_port is None:
                local_port = 0
            else:
                local_port = self._parameters.client_port

            connect_params['local_addr'] = (local_addr, local_port)

        # IP Version
        if self._parameters.ip_version == 4:
            connect_params['family'] = socket.AF_INET

        elif self._parameters.ip_version == 6:
            connect_params['family'] = socket.AF_INET6

        self._logger.debug('Connect params: %s', connect_params)

        # Try to connect
        num_retries = 1
        while num_retries > 0:
            try:
                control_connect_coro = self._loop.create_connection(
                    lambda: ControlProtocol(test=self),
                    **connect_params)
                self._loop.create_task(control_connect_coro)
                break
            except Exception as exc:
                self._logger.exception('Exception connecting to the server!', exc_info=exc)
                time.sleep(1)
                num_retries -= 1

        if num_retries == 0:
            self._logger.error('Failed to connect to the server!')
            return -1