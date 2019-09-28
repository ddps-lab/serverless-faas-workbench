import os
import subprocess


def function_handler(request):
    request_json = request.get_json(silent=True)
    bs = 'bs='+request_json['bs']
    count = 'count='+request_json['count']
    print(bs)
    print(count)
    out_fd = open('/tmp/io_write_logs','w')
    a = subprocess.Popen(['dd', 'if=/dev/zero', 'of=/tmp/out', bs, count], stderr=out_fd)
    a.communicate()
    
    output = subprocess.check_output(['ls', '-alh', '/tmp/'])
    print(output)

    output = subprocess.check_output(['du', '-sh', '/tmp/'])
    print(output)
                               
    with open('/tmp/io_write_logs') as logs:
        result = str(logs.readlines()[2]).replace('\n', '')
        print(result)
        return result