FROM openwhisk/actionloop-python-v3.6-ai:1.16.0

COPY ops.py ops.py
COPY setup.py setup.py
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip &&\
    pip3 install --no-cache-dir -r requirements.txt &&\
    ln -sf /usr/bin/python3 /usr/local/bin/python
RUN pip3 install -e .