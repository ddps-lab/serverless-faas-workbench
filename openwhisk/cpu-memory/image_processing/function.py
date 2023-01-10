import boto3
import uuid
from time import time
from PIL import Image

import ops

FILE_NAME_INDEX = 1


def image_processing(file_name, image_path):
    path_list = []
    start = time()
    with Image.open(image_path) as image:
        tmp = image
        path_list += ops.flip(image, file_name)
        path_list += ops.rotate(image, file_name)
        path_list += ops.filter(image, file_name)
        path_list += ops.gray_scale(image, file_name)
        path_list += ops.resize(image, file_name)

    latency = time() - start
    print("PATH_LIST", path_list)
    return latency, path_list


def main(event):
    latencies = {}
    timestamps = {}
    timestamps["starting_time"] = time()

    input_bucket = event['input_bucket']
    object_key = event['object_key']
    output_bucket = event['output_bucket']
    endpoint_url = event['endpoint_url']
    aws_access_key_id = event['aws_access_key_id']
    aws_secret_access_key = event['aws_secret_access_key']
    metadata = event['metadata']

    s3_client = boto3.client('s3',
                    endpoint_url=endpoint_url,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)#,                                                                                                                                                                                                                                                                                                            
                    #config=Config(signature_version='s3v4'),                                                                                                                                                                                                                                                                                                                 
                    #region_name='us-east-1')   
    start = time()
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), object_key)
    s3_client.download_file(input_bucket, object_key, download_path)
    download_latency = time() - start
    latencies["download_data"] = download_latency

    image_processing_latency, path_list = image_processing(object_key, download_path)
    latencies["function_execution"] = image_processing_latency
    print("PATH_LIST OUTSIDE", path_list)

    start = time()
    for upload_path in path_list:
        s3_client.upload_file(upload_path, output_bucket, upload_path.split("/")[FILE_NAME_INDEX])
    upload_latency = time() - start
    latencies["upload_data"] = upload_latency
    timestamps["finishing_time"] = time()

    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}
