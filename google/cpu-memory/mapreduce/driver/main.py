from google.cloud import storage
import gcsfs
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
import time
import json
import requests


total_map = 0
total_network = 0


def map_invoke_lambda(job_bucket, dataset_bucket, all_keys, batch_size, mapper_id):
    global total_map, total_network

    keys = all_keys[mapper_id*batch_size: (mapper_id+1)*batch_size]
    key = ""
    for item in keys:
        key += item +'/'
    key = key[:-1]
    
    mapper_url = "[YOUR MAPPER HTTP TRIGGER URL]"
    payload = {
        'job_bucket': job_bucket,
        'dataset_bucket': dataset_bucket,
        'dataset_keys': key,
        'mapper_id': mapper_id
    }
    
    response = requests.post(mapper_url, json=payload)
    print(response.text)

    output = json.loads(response.text)
    total_map += float(output['map'])
    total_network += float(output['network'])


def reduce_invoke_lambda(job_bucket):
    reducer_url = "[YOUR REDUCER HTTP TRIGGER URL]"

    payload = {
        'job_bucket': job_bucket
    }

    response = requests.post(reducer_url, json=payload)
    print(response.text)


def function_handler(request):
    request_json = request.get_json(silent=True)
    job_bucket = request_json['job_bucket']
    dataset_bucket = request_json['dataset_bucket']
    n_mapper = int(request_json['n_mapper'])
    
    storage_client = storage.Client()
    d_bucket = storage_client.get_bucket(dataset_bucket)
    j_bucket = storage_client.get_bucket(job_bucket)

    # Fetch all the keys
    dataset_blobs = d_bucket.list_blobs()
    all_keys = []
    for d_blob in dataset_blobs:
        all_keys.append(d_blob.name)

    total_size = len(all_keys)
    batch_size = 1
    print("dataset file : " + str(all_keys))
    print("key name : " + str(all_keys))
    print("# of Mappers ", n_mapper)
    
    if total_size % n_mapper == 0:
        batch_size = int(total_size/n_mapper)
    else:
        batch_size = int(total_size/n_mapper) + 1
    
    for idx in range(n_mapper):
        print("mapper-" + str(idx) + ":" + str(all_keys[idx * batch_size: (idx+1) * batch_size]))
    
    # Invoke Mapper
    pool = ThreadPool(n_mapper)
    invoke_lambda_partial = partial(map_invoke_lambda, job_bucket, dataset_bucket, all_keys, batch_size)
    pool.map(invoke_lambda_partial, range(n_mapper))
    pool.close()
    pool.join()

    # Check Mapper Done
    while True:
        job_blobs = j_bucket.list_blobs()
        done = sum(1 for _ in job_blobs)

        time.sleep(10)
        if done == total_size:
            break

    print("[*] Map Done - map : " + str(total_map) + " network : " + str(total_network))

    # Reducer
    reduce_invoke_lambda(job_bucket)
