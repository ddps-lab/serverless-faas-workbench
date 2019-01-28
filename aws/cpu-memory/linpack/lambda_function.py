from numpy import matrix, array, linalg, random, amax, asscalar
from time import time

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

    R=A*X-B

    Rs=asscalar(max(abs(R.A)))

    nx=asscalar(max(abs(X)))

    mflops = (ops*1e-6/latency)

    result = {
    	'mflops': mflops,
    	'latency': latency
    }

	return result

def lambda_handler(event, context):
    N = int(event['N'])
    result = linpack(N)
    print(result)
    return result
