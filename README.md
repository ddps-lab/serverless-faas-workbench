![function_bench_title](./docs/images/function_bench_title.png)

## PUBLICATION
_Jeongchul Kim and Kyungyong Lee, 'Function Bench : A Suite of Workloads for Serverless Cloud Function Service',
IEEE International Conference on Cloud Computing 2019, 07/2019 [pdf](https://kimjeongchul.github.io/assets/paper/FunctionBench%20-%20A%20Suite%20of%20Workloads%20for%20Serverless%20Cloud%20Function%20Service.pdf)_

_Jeongchul Kim and Kyungyong Lee, 'Practical Cloud Workloads for Serverless FaaS, ACM Symposium on Cloud Computing 2019, 11/2019_ [pdf](https://dl.acm.org/citation.cfm?id=3365439)

The FunctionBench is composed of micro benchmark and application workload; 
the micro-benchmark uses simple system calls to measure performance of resources exclusively, 
and the application-benchmark represents realistic data-oriented applications that generally utilize various resources together. 
With the introduction of FunctionBench, we believe that researchers can easily deploy function applications to evaluate their proposed systems and algorithms justly. 
To the best of our knowledge, the proposed FunctionBench is the first publicly available realistic FaaS workload suites that are ready to be deployed on public cloud services.

- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Google Cloud Functions](https://cloud.google.com/functions/) 
- [Azure Functions](https://azure.microsoft.com/en-us/services/functions/)

## FunctionBench workloads
### 1. CPU & Memory
 - [Float Operations(sin, cos, sqrt)](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/float-operation)
 - [MatMul(square matrix multiplication)](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/matmul)
 - [Linpack(solve linear equations Ax = b)](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/linpack)
 - [Image Processing](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/image-processing)
 - [Video Processing](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/video-processing)
 - [MapReduce](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/mapreduce)
 - [Chameleon](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/chameleon)
 - [pyaes](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/pyaes)
 - [Feature Generation](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/feature-generation)
 - [Model Training](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/model-training)
 - Model Serving
    - [Video Face Detection - Cascade Classifier](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/video-face-detection)
    - [Classification Image - CNN](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/classification-image)
    - [Generating Names- RNN](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/generating-names-rnn)
    - [Prediction Reviews - LR](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/ml_lr_prediction)
 
### 2. Disk
 - [dd](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/dd)
 - [gzip-compression](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/gzip-compression)

### 3. Network
 - [iPerf3](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/iperf3)
 - [Cloud storage service download-upload](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/cloud-storage)
 - [json serialization deserialization](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/json)
 
## Required Cloud Service
### AWS
 - [AWS Lambda](https://aws.amazon.com/lambda/)
 - [AWS EC2](https://aws.amazon.com/ec2/)
 - [AWS S3](https://aws.amazon.com/s3/)
 - [AWS Step Functions](https://aws.amazon.com/step-functions/)
 - [AWS IAM](https://aws.amazon.com/iam/)
 
### Google Cloud
 - [Google Cloud Functions](https://cloud.google.com/functions/) 
 - [Google Cloud Buckets](https://cloud.google.com/storage/)

### Azure
 - [Azure Functions](https://azure.microsoft.com/en-us/services/functions/)
 - [Azure Storage](https://docs.microsoft.com/en-us/azure/storage/common/storage-introduction)
 
