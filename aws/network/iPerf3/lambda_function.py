import asyncio
import logging
from py3iperf3.iperf3_client import Iperf3Client
from py3iperf3.iperf3_api import Iperf3TestProto
from py3iperf3.utils import setup_logging

def get_log():
    log =  open("/tmp/log.out").readlines()
    log = "".join(log)
    return log

def lambda_handler(event, context):
    params = {}
    params['protocol'] = Iperf3TestProto.TCP
    params['server_address'] = event['address']
    params['server-port'] = event['port']
    params['test_duration'] = event['num_test']
    params['get-server-output'] = True
    params['parallel'] = 26
    setup_logging(**params)
        
    loop = asyncio.get_event_loop()
    
    iperf3_client = Iperf3Client(loop=loop)
    iperf3_client.create_test(test_parameters=params)
    
    loop.call_soon(iperf3_client.run_all_tests)
    loop.run_forever()
    
    iperf3_client.stop_all_tests()
    
    log = get_log()
    print(log)
    return log
    
   