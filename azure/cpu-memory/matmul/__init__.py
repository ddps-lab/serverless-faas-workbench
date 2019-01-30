import azure.functions as func
import numpy as np
from time import time
import logging

def matmul(N):
    A = np.random.rand(N, N)
    B = np.random.rand(N, N)

    start = time()
    C = np.matmul(A, B)
    latency = time() - start

    return latency

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    N = req.params.get('N')
    N = int(N)
    latency = matmul(N)
    logging.info(latency)
    return func.HttpResponse(str(latency))