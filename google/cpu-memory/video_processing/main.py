from google.cloud import storage
from time import time
import cv2

def video_processing(blob_name, file_path):
    output_file_path = '/tmp/output-' + blob_name
    video = cv2.VideoCapture(file_path)
    
    width = int(video.get(3))
    height = int(video.get(4))
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file_path, fourcc, 20.0, (width, height))
    
    start = time()
    while(video.isOpened()):
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            im = cv2.imwrite('/tmp/frame.jpg', gray_frame)
            gray_frame = cv2.imread('/tmp/frame.jpg')
            out.write(gray_frame)
        else:
            break
            
    latency = time() - start
    
    video.release()
    out.release()
    return latency, output_file_path

def download_blob(blob, download_path):
    blob.download_to_filename(download_path)
    print('Blob {} downloaded to {}.'.format(
        blob.name,
        download_path))

def upload_blob(bucket_name, blob, upload_path):
    blob.upload_from_filename(upload_path)
    print('File {} uploaded to {}.'.format(
        blob.name,
        bucket_name))
    
def function_handler(request):
    request_json = request.get_json(silent=True)
    src_bucket = request_json['src_bucket']
    blob_name = request_json['blob_name']
    dst_bucket = request_json['dst_bucket']
    
    storage_client = storage.Client()
    s_bucket = storage_client.get_bucket(src_bucket)
    s_blob = s_bucket.blob(blob_name)
    
    download_path = "/tmp/" + blob_name
    download_blob(s_blob, download_path)
    
    latency, upload_path = video_processing(blob_name, download_path)
    
    d_bucket = storage_client.get_bucket(dst_bucket)
    d_blob = d_bucket.blob(blob_name)
    upload_blob(dst_bucket, d_blob, upload_path)
    
    return "latency : " + str(latency)