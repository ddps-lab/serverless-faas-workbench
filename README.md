# Serverless-faas-workbench
The FunctionBench is composed of micro benchmark and application workload; 
the micro-benchmark uses simple system calls to measure performance of resources exclusively, 
and the application-benchmark represents realistic data-oriented applications that generally utilize various resources together. 
With the introduction of FunctionBench, we believe that researchers can easily deploy function applications to evaluate their proposed systems and algorithms justly. 
To the best of our knowledge, the proposed FunctionBench is the first publicly available realistic FaaS workload suites that are ready to be deployed on public cloud services.

- AWS Lambda
- Google Cloud Functions
- Azure Functions

## FunctionBench workloads
### 1. CPU & Memory
 - Float Operations(sin, cos, sqrt)
 - MatMul(square matrix multiplication)
 - Linpack(solve linear equations Ax = b)
 - Image Processing
 - Video Processing
 - Feature Generation
 - Model Training
 - Model Serving
 -- Video Face Detection - Cascade Classifier
 -- Classification Image - CNN
 -- Generating Names- RNN
 -- Prediction Reviews - LR
 
### 2. Disk
 - dd

### 3. Network
 - iPerf3
 - Cloud storage service download-upload
 
## Required Cloud Service
### AWS
 - EC2
 - S3
 - Step Functions
 - IAM
 
### Google Cloud
 - Google Cloud Buckets

### Azure
 - Azure Storage
