FROM bitnami/python:3.12

RUN apt update && \
    apt install -qq -y jq curl iputils-ping fping pkg-config default-libmysqlclient-dev

RUN python3 -m venv venv

COPY requirements.txt .
RUN venv/bin/pip3 install -r requirements.txt

COPY build/ .

ENTRYPOINT [ "venv/bin/uvicorn", "demo.asgi:application", "--host", "0.0.0.0", "--port", "80"]

