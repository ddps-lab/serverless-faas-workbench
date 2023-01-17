import numpy as np
from time import time


def matmul(n):
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)

    start = time()
    C = np.matmul(A, B)
    latency = time() - start
    return latency


def main(event):
    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    n = int(event['n'])
    metadata = event['metadata']
    result = matmul(n)
    latencies["function_execution"] = result
    timestamps["finishing_time"] = time()

    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}
