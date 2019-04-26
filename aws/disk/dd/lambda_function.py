import subprocess

tmp = '/tmp'

"""
dd - convert and copy a file
man : http://man7.org/linux/man-pages/man1/dd.1.html

Options 
 - bs=BYTES
    read and write up to BYTES bytes at a time (default: 512);
    overrides ibs and obs
 - if=FILE
    read from FILE instead of stdin
 - of=FILE
    write to FILE instead of stdout
 - count=N
    copy only N input blocks
"""


def lambda_handler(event, context):
    bs = 'bs='+event['bs']
    count = 'count='+event['count']

    out_fd = open(tmp + 'io_write_logs', 'w')
    dd = subprocess.Popen(['dd', 'if=/dev/zero', 'of=/tmp/out', bs, count], stderr=out_fd)
    dd.communicate()
    
    subprocess.check_output(['ls', '-alh', tmp])

    with open(tmp + 'io_write_logs') as logs:
        result = str(logs.readlines()[2]).replace('\n', '')
        return result
