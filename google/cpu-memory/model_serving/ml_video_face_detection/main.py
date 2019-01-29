from google.cloud import storage
from time import time
import cv2

def video_processing(model_path, blob_name, file_path):
    output_file_path = '/tmp/output-' + blob_name
    video = cv2.VideoCapture(file_path)
    
    width = int(video.get(3))
    height = int(video.get(4))
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file_path, fourcc, 20.0, (width, height))
    
    face_cascade = cv2.CascadeClassifier(model_path)
    
    start = time()
    while(video.isOpened()):
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
            print("Found {0} faces!".format(len(faces)))
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            out.write(frame)
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
    model_bucket = request_json['model_bucket']
    model_blob_name = request_json['model_blob_name']
    
    
    storage_client = storage.Client()
    m_bucket = storage_client.get_bucket(model_bucket)
    m_blob = m_bucket.blob(model_blob_name)
    
    model_path = "/tmp/" + model_blob_name
    download_blob(m_blob, model_path)
    
    s_bucket = storage_client.get_bucket(src_bucket)
    s_blob = s_bucket.blob(blob_name)
    
    download_path = "/tmp/" + blob_name
    download_blob(s_blob, download_path)
    
    latency, upload_path = video_processing(model_path, blob_name, download_path)
    
    d_bucket = storage_client.get_bucket(dst_bucket)
    d_blob = d_bucket.blob(blob_name)
    upload_blob(dst_bucket, d_blob, upload_path)
    
    return "latency : " + str(latency)