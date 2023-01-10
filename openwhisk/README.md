# FunctionBench workloads adapted to OpenWhisk

## Creating and Invoking Actions (functions)

### Creating Actions

To create actions:

- Using **Docker Images**:

    `` wsk action create $action_name --docker $docker_image_registry_url $path_to_action/function.py  -[$arg_list] ``

- Without Docker Images:

    `` wsk action create $action_name $path_to_action/function.py -[$arg_list] ``

### Invoking Actions
To invoke actions:
    ``wsk action invoke $action_name [-p $param_name $param_value] -[$arg_list]``

### Examples

 - Float Operation

    - Create:
       `` wsk action create floatoperation cpu-memory/float_operation/function.py -i ``

    - Invoke:
       `` wsk action invoke floatoperation -p n 10000000 -i ``

 - Chameleon
    - Create:
        `` wsk action create chameleon --docker andersonandrei/python3action:chameleon cpu-memory/chameleon/function.py -i ``

    - Invoke:
        `` wsk action invoke chameleon -p num_of_rows 20000 -p num_of_cols 20000 -i ``

 - Video Processing

    - Create:
        `` wsk action create videoprocessing --docker andersonandrei/python3action:videoprocessing cpu-memory/video_processing/function.py -i ``

    - Invoke:
        `` wsk action invoke videoprocessing -p object_key "SampleVideo_1280x720_10mb.mp4" -p input_bucket "input" -p output_bucket "output" -p endpoint_url "http://minio.default:9000" -p aws_access_key_id "access-key-id" -p aws_secret_access_key "secret-access-key" -i ``

## Functions Parameter Descriptions

To find examples of data source for each function, please clik on the corresponding urls.

- [Floatoperation](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/float-operation):
    - n: [NUMBER]

- [Linpack](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/linpack):
    - n: [NUMBER] 

- [Chameleon](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/chameleon):
    - num_of_rows: [NUMBER] 
    - num_of_cols: [NUMBER]

- [Matmul](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/matmul):
    - n: [NUMBER]

- [Pyaes](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/pyaes):
    - length_of_message: [NUMBER]
    - num_of_iterations: [NUMBER]     

- [Video Processing](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/video-processing):
    - object_key: [OBJECT_KEY_NAME]
    - input_bucket: [INPUT_BUCKET_NAME]
    - output_bucket: [OUTPUT_BUCKET_NAME] 
    - endpoint_url: [ENDPOINT_URL] 
    - aws_access_key_id: [BUCKET_ACCESS_KEY_ID] 
    - aws_secret_access_key: [BUCKET_SECRET_KEY_ID]

- [Image Processing](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/image-processing):
    - object_key: [OBJECT_KEY_NAME] 
    - input_bucket: [INPUT_BUCKET_NAME] 
    - output_bucket: [OUTPUT_BUCKET_NAME] 
    - endpoint_url: [ENDPOINT_URL] 
    - aws_access_key_id: [BUCKET_ACCESS_KEY_ID] 
    - aws_secret_access_key: [BUCKET_SECRET_KEY_ID]

- [Model Training](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/model-training):
    - dataset_bucket: [INPUT_BUCKET_NAME] 
    - dataset_object_key: [DATASET_OBJECT_KEY]
    - output_bucket: [OUTPUT_BUCKET_NAME] 
    - model_object_key: lr_model.pk
    - endpoint_url: [ENDPOINT_URL] 
    - aws_access_key_id: [BUCKET_ACCESS_KEY_ID] 
    - aws_secret_access_key: [BUCKET_SECRET_KEY_ID]

- [Face Detection](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/video-face-detection):
    - object_key: [OBJECT_KEY_NAME]
    - input_bucket: [INPUT_BUCKET_NAME]
    - output_bucket: [OUTPUT_BUCKET_NAME]
    - model_bucket: [INPUT_BUCKET_NAME]
    - model_object_key: [MODEL_OBJECT_KEY]
    - endpoint_url: [ENDPOINT_URL] 
    - aws_access_key_id: [BUCKET_ACCESS_KEY_ID] 
    - aws_secret_access_key: [BUCKET_SECRET_KEY_ID]

- [Rnn Generate](https://github.com/kmu-bigdata/serverless-faas-workbench/wiki/generating-names-rnn):
    - language: [LANGUAGE]
    - start_letters: [START_LETTERS]
    - model_bucket: [INPUT_BUCKET_NAME]
    - model_object_key: [MODEL_OBJECT_KEY]
    - model_parameter_object_key: [MODEL_PARAMETER_OBJECT_KEY]
    - endpoint_url: [ENDPOINT_URL] 
    - aws_access_key_id: [BUCKET_ACCESS_KEY_ID] 
    - aws_secret_access_key: [BUCKET_SECRET_KEY_ID]