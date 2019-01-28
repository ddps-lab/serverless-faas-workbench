"""
Default run settings
"""

from py3iperf3.iperf3_api import Iperf3TestProto

class Iperf3TestSettings(object):
    """Default settings of a test"""

    test_protocol = Iperf3TestProto.TCP
    server_address = ''
    server_port = 5201

    client_address = None
    client_port = None
    block_size = None
    ip_version = 4
    test_duration = 10
    report_interval = 1
    no_delay = False
    parallel = 1
    reverse = False
    title = None
    format = None
    blockcount = None
    bytes = None
    file = None
    udp64bitcounters = False
    get_server_output = False
    window = None

    # Server specific options
    server = False
    one_off = False
    daemon = False
    pidfile = None

    # The following attributes are ignored
    log_filename = None
    debug = None