FROM openwhisk/python3action:95f1358

COPY requirements.txt requirements.txt
RUN apk add --update py-pip
RUN pip install -r requirements.txt