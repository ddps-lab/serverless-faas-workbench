import subprocess
import json

"""
iPerf3 :  The ultimate speed test tool for TCP, UDP and SCTP
doc : https://iperf.fr/iperf-doc.php
"""

kilo = 1000
byte = 8


def network_test(server_ip, server_port, test_time, reverse):
    reverse_option = ""
    if reverse:
        reverse_option = "R"

    sp = subprocess.Popen(["./iperf3",
                           "-c",
                           server_ip,
                           "-p",
                           str(server_port),
                           reverse_option,
                           "-t",
                           test_time,
                           "-Z",
                           "-J"
                           ],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    out, err = sp.communicate()

    end = json.loads(out)["end"]

    sender = end["sum_sent"]
    receiver = end["sum_received"]

    send_mbit_s = sender["bits_per_second"] / kilo / kilo / byte
    recv_mbit_s = receiver["bits_per_second"] / kilo / kilo / byte

    return send_mbit_s, recv_mbit_s


def lambda_handler(event, context):
    server_ip = event['server_ip']
    server_port = event['server_port']
    test_time = event['test_time']
    reverse = event['reverse']

    send_mbit_s, recv_mbit_s = network_test(server_ip, server_port, test_time, reverse)

    return {'send_mbit_s': send_mbit_s, 'recv_mbit_s': recv_mbit_s}
