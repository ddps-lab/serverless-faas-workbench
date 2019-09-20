from time import time
import gzip


def lambda_handler(event, context):
    num_of_data = event['num_of_data']
    data = "Hello World!" * num_of_data

    start = time()
    with gzip.open('/tmp/result.gz', 'wb') as gz:
        gz.writelines(data)
    compress_latency = time() - start

    print(compress_latency)
    return compress_latency
