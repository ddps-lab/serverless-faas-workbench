import numpy as np
from time import time

def matmul(N):
	A = np.random.rand(N, N)
	B = np.random.rand(N, N)

	start = time()
    C = np.matmul(A, B)
    latency = time() - start

    return latency

def lambda_handler(event, context):
    N = int(event['N'])
    result = matmul(N)
    print(result)
    return result