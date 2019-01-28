"""
Various constants from the official C implementation of iPerf3.
"""
import enum
import socket

COOKIE_SIZE = 36
DEFAULT_BLOCK_TCP = 128 * 1024
DEFAULT_BLOCK_UDP = 1 * 1024

class Iperf3TestProto(enum.Enum):
    """Protocol used to trasmit test data"""
    TCP = socket.SOCK_STREAM
    UDP = socket.SOCK_DGRAM
    SCTP = 12

class Iperf3State(enum.Enum):
    """iPerf3 test state"""
    TEST_START = 1
    TEST_RUNNING = 2
    RESULT_REQUEST = 3
    TEST_END = 4
    STREAM_BEGIN = 5
    STREAM_RUNNING = 6
    STREAM_END = 7
    ALL_STREAMS_END = 8
    PARAM_EXCHANGE = 9
    CREATE_STREAMS = 10
    SERVER_TERMINATE = 11
    CLIENT_TERMINATE = 12
    EXCHANGE_RESULTS = 13
    DISPLAY_RESULTS = 14
    IPERF_START = 15
    IPERF_DONE = 16
    ACCESS_DENIED = -1
    SERVER_ERROR = -2