import azure.functions as func
from azure.storage.blob import BlockBlobService, PublicAccess
from PIL import Image, ImageFilter
import logging
from time import time

TMP = "/tmp/"


def flip(image, file_name):
    path_list = []
    path = TMP + "flip-left-right-" + file_name
    img = image.transpose(Image.FLIP_LEFT_RIGHT)
    img.save(path)
    path_list.append(path)

    path = TMP + "flip-top-bottom-" + file_name
    img = image.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path)
    path_list.append(path)

    return path_list


def rotate(image, file_name):
    path_list = []
    path = TMP + "rotate-90-" + file_name
    img = image.transpose(Image.ROTATE_90)
    img.save(path)
    path_list.append(path)

    path = TMP + "rotate-180-" + file_name
    img = image.transpose(Image.ROTATE_180)
    img.save(path)
    path_list.append(path)

    path = TMP + "rotate-270-" + file_name
    img = image.transpose(Image.ROTATE_270)
    img.save(path)
    path_list.append(path)

    return path_list


def filter(image, file_name):
    path_list = []
    path = TMP + "blur-" + file_name
    img = image.filter(ImageFilter.BLUR)
    img.save(path)
    path_list.append(path)

    path = TMP + "contour-" + file_name
    img = image.filter(ImageFilter.CONTOUR)
    img.save(path)
    path_list.append(path)

    path = TMP + "sharpen-" + file_name
    img = image.filter(ImageFilter.SHARPEN)
    img.save(path)
    path_list.append(path)

    return path_list


def gray_scale(image, file_name):
    path = TMP + "gray-scale-" + file_name
    img = image.convert('L')
    img.save(path)

    return [path]


def resize(image, file_name):
    path = TMP + "resized-" + file_name
    image.thumbnail((128, 128))
    image.save(path)

    return [path]


def image_processing(file_name, image_path):
    path_list = []
    start = time()
    with Image.open(image_path) as image:
        path_list += flip(image, file_name)
        path_list += rotate(image, file_name)
        path_list += filter(image, file_name)
        path_list += gray_scale(image, file_name)
        path_list += resize(image, file_name)

    latency = time() - start

    return latency, path_list


def main(req: func.HttpRequest) -> func.HttpResponse:
    acc_name = req.params.get('account_name')
    acc_key = req.params.get('account_key')
    container_name = req.params.get('container_name')
    blob_name = req.params.get('blob_name')

    block_blob_service = BlockBlobService(account_name=acc_name, account_key=acc_key)
    logging.info(block_blob_service)
    block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)
    generator = block_blob_service.list_blobs(container_name)
    for blob in generator:
        logging.info("\t Blob name: " + blob.name)

    download_path = "/tmp/" + blob_name
    block_blob_service.get_blob_to_path(container_name, blob_name, download_path)
    logging.info("Downloading blob to " + download_path)
    
    latency, path_list = image_processing(blob_name, download_path)

    for upload_path in path_list:
        block_blob_service.create_blob_from_path(container_name, upload_path.split("/")[2], upload_path)

    return func.HttpResponse(str(latency))
