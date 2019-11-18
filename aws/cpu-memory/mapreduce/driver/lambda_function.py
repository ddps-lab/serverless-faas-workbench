import boto3
import json
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
import time

# Create AWS resource and client
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

total_map = 0
total_network = 0


def map_invoke_lambda(job_bucket, bucket, all_keys, batch_size, mapper_id):
    keys = all_keys[mapper_id * batch_size: (mapper_id + 1) * batch_size]
    key = ""
    for item in keys:
        key += item + '/'
    key = key[:-1]

    response = lambda_client.invoke(
        FunctionName='mapper',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "job_bucket": job_bucket,
            "bucket": bucket,
            "keys": key,
            "mapper_id": mapper_id
        })
    )
    output = eval(response['Payload'].read())
    print("mapper output : ", output)

    json_data = json.loads(output)

    global total_map, total_network
    total_map += float(json_data['map'])
    total_network += float(json_data['network'])


def reduce_invoke_lambda(job_bucket):
    response = lambda_client.invoke(
        FunctionName='reducer',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "job_bucket": job_bucket
        })
    )
    output = eval(response['Payload'].read())
    print("reducer output : ", output)


def lambda_handler(event, context):
    job_bucket = event['job_bucket']
    src_bucket = event['bucket']
    n_mapper = event['n_mapper']

    # Fetch all the keys
    all_keys = []
    for obj in s3.Bucket(src_bucket).objects.all():
        all_keys.append(obj.key)

    print("dataset file : " + str(len(all_keys)))
    print("key name : " + str(all_keys))

    print("# of Mappers ", n_mapper)
    total_size = len(all_keys)
    batch_size = 0

    if total_size % n_mapper == 0:
        batch_size = total_size / n_mapper
    else:
        batch_size = total_size // n_mapper + 1

    for idx in range(n_mapper):
        print("mapper-" + str(idx) + ":" + str(all_keys[idx * batch_size: (idx + 1) * batch_size]))

    pool = ThreadPool(n_mapper)
    invoke_lambda_partial = partial(map_invoke_lambda, job_bucket, src_bucket, all_keys, batch_size)
    pool.map(invoke_lambda_partial, range(n_mapper))
    pool.close()
    pool.join()

    while True:
        job_keys = s3_client.list_objects(Bucket=job_bucket)["Contents"]
        print("Wait Mapper Jobs ...")
        time.sleep(5)
        if len(job_keys) == len(all_keys):
            print("[*] Map Done : mapper " + str(len(job_keys)) + " finished.")
            break

    print("[*] Map Done - map : " + str(total_map) + " network : " + str(total_network))

    # Reducer
    reduce_invoke_lambda(job_bucket)
    print("[*] Reduce Done : reducer finished.")

    return 'MapReduce done'
