import boto3
import uuid
from time import time
import cv2

tmp = "/tmp/"
FILE_NAME_INDEX = 0
FILE_PATH_INDEX = 2


def video_processing(object_key, video_path, model_path):
    file_name = object_key.split(".")[FILE_NAME_INDEX]
    result_file_path = tmp+file_name+'-detection.avi'

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height))

    face_cascade = cv2.CascadeClassifier(model_path)

    start = time()
    while video.isOpened():
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
            #print("Found {0} faces!".format(len(faces)))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            out.write(frame)
        else:
            break

    latency = time() - start

    video.release()
    out.release()

    return latency, result_file_path


def main(event):
    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    
    input_bucket = event['input_bucket']
    object_key = event['object_key']
    output_bucket = event['output_bucket']
    model_object_key = event['model_object_key'] # example : haarcascade_frontalface_default.xml
    model_bucket = event['model_bucket'] # input_bucket as well
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

    download_path = tmp+'{}{}'.format(uuid.uuid4(), object_key)
    model_path = tmp + '{}{}'.format(uuid.uuid4(), model_object_key)

    start = time()
    s3_client.download_file(input_bucket, object_key, download_path)
    s3_client.download_file(model_bucket, model_object_key, model_path)    
    download_data = time() - start
    latencies["download_data"] = download_data

    function_execution, upload_path = video_processing(object_key, download_path, model_path)
    latencies["function_execution"] = download_data

    start = time()
    s3_client.upload_file(upload_path, output_bucket, upload_path.split("/")[FILE_PATH_INDEX])
    upload_data = time() - start
    latencies["upload_data"] = upload_data
    timestamps["finishing_time"] = time()

    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}