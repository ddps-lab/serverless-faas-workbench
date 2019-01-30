import azure.functions as func
from numpy import matrix, array, linalg, random, amax, asscalar
from time import time
import logging

def linpack(N):
    eps=2.22e-16

    ops=(2.0*N)*N*N/3.0+(2.0*N)*N

    # Create AxA array of random numbers -0.5 to 0.5
    A=random.random_sample((N,N))-0.5
    B=A.sum(axis=1)

    # Convert to matrices
    A=matrix(A)

    B=matrix(B.reshape((N,1)))
    na=amax(abs(A.A))

    start = time()
    X=linalg.solve(A,B)
    latency = time() - start

    mflops = (ops*1e-6/latency)

    result = {
        'mflops': mflops,
        'latency': latency
    }

    return result


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    N = req.params.get('N')
    N = int(N)
    latency = linpack(N)
    logging.info(latency)
    return func.HttpResponse(str(latency))