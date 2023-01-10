FROM openwhisk/actionloop-python-v3.6-ai:1.16.0

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip &&\
    pip3 install --no-cache-dir -r requirements.txt &&\
    ln -sf /usr/bin/python3 /usr/local/bin/python

