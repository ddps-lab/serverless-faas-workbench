from time import time
import gzip
import os


def lambda_handler(event, context):
    file_size = event['file_size']
    file_write_path = '/tmp/file'

    start = time()
    with open(file_write_path, 'wb') as f:
        f.write(os.urandom(file_size * 1024 * 1024))
    disk_latency = time() - start

    with open(file_write_path) as f:
        start = time()
        with gzip.open('/tmp/result.gz', 'wb') as gz:
            gz.writelines(f)
        compress_latency = time() - start

    print(compress_latency)

    return {'disk_write': disk_latency, "compress": compress_latency}
