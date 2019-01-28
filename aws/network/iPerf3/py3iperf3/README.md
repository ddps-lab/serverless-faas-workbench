[![Build Status](https://img.shields.io/travis/justas-/py3iperf3.svg)](https://travis-ci.org/justas-/py3iperf3) [![Coverage Status](https://img.shields.io/coveralls/github/justas-/py3iperf3.svg)](https://coveralls.io/github/justas-/py3iperf3?branch=master)

# Py3iPerf3 - A native Python iPerf3 client
https://github.com/justas-/py3iperf3

Py3iPerf3 is a clone of iPerf3 network performance measurement tool implemented in pure Python. The client is network-protocol compatible with the [original iPerf3](https://github.com/esnet/iperf) maintained by ESnet and written in C. Py3iPerf3 can be used as a stand-alone application, or as a library in your application.

### N.B.

This is work in progress. At the moment, the client supports working as a client (i.e. not server) and can send and receive data using TCP and UDP. 

### Running as a stand-alone application

As with iPerf3, py3iPerf3 can work as a stand-alone command-line application. It is configured by passing command line parameters. You can get the whole list of supported parameters by invoking py3iPerf3 with a "-h" option: ```python3 iperf.py -h```.

Additionally, all supported options are listed here as well:

```
--server-address <IP Address/Hostname> # IP address or hostname of the server
--server-port <Port>                   # Port of the server. Defaults to 5201
--client-port <Port>                   # Bind client to the given port. Defaults to ephemeral port.
--ip-version <4|6>                     # Connect using the indicated IP version
--test-duration <Sec>                  # How long to run the test. Default is 10 seconds
--debug                                # Enable debug output
--log-filename <Path>                  # Log to the indicated file
--parallel <N>                         # Send data on this number of parallel streams
--blockcount <N>                       # Number of blocks to send
--reverse                              # Reverse data direction (server sends data)
--protocol <TCP|UDP>                   # Data transport protocol. Defaults to TCP
--no-delay                             # Disable Nagle's algorithm
--title <Text>                         # Add free text to the results
--get-server-output                    # Get results from the server
--window <Size>                        # Set the data socket buffer size in Bytes
```

### Running as a library

The following example shows how to run the client as a library:

```python
import asyncio

from py3iperf3.iperf3_client import Iperf3Client
from py3iperf3.test_settings import TestSettings

loop = asyncio.get_event_loop()
params = TestSettings() 

# Do any changes to the defaults as required
params.server_address = '127.0.0.1'
params.test_duration = 60

iperf3_client = Iperf3Client(loop=loop)
iperf3_test = iperf3_client.create_test(test_parameters=params)

try:
   loop.call_soon(iperf3_client.run_all_tests)
   loop.run_forever()
except KeyboardInterrupt:
   pass

iperf3_client.stop_all_tests()
loop.close()
```

### Performance

Py3iPerf3 is based on asyncio library and its performance is only as good as the performance of the event loop implementation. Furthermore, even if using parallel connections, the application is single-threaded and all parallel connections are run on a single thread. In the (near?) future, the code will be updated to support running data connections in their own dedicated processes.

### License and contributing

The code of py3iPerf3 is released under the MIT license. Contributions are encouraged via GitHub.
