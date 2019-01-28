import boto3
import os
import subprocess

def lambda_handler(event, context):
    bs = 'bs='+event['bs']
    count = 'count='+event['count']
    print(bs)
    print(count)
    out_fd = open('/tmp/io_write_logs','w')
    a = subprocess.Popen(['dd', 'if=/dev/zero', 'of=/tmp/out', bs, count], stderr=out_fd)
    a.communicate()
    
    output = subprocess.check_output(['ls', '-alh', '/tmp/'])
    print(output)
    with open('/tmp/io_write_logs') as logs:
        l = str(logs.readlines()[2]).replace('\n', '')
        print(l)
        return l