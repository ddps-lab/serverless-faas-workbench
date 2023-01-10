from numpy import matrix, linalg, random
from time import time


def linpack(n):
    # LINPACK benchmarks
    ops = (2.0 * n) * n * n / 3.0 + (2.0 * n) * n

    # Create AxA array of random numbers -0.5 to 0.5
    A = random.random_sample((n, n)) - 0.5
    B = A.sum(axis=1)

    # Convert to matrices
    A = matrix(A)
    B = matrix(B.reshape((n, 1)))

    # Ax = B
    start = time()
    x = linalg.solve(A, B)
    latency = time() - start

    mflops = (ops * 1e-6 / latency)

    return latency, mflops


def main(event):
    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    n = int(event['n'])
    metadata = event['metadata']
    latency, mflops = linpack(n)
    latencies["function_execution"] = latency
    timestamps["finishing_time"] = time()

    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}