FROM python:3.9.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY containers/requirements.txt /tmp/requirements.txt
WORKDIR /root/workspace

RUN pip install --upgrade pip setuptools \
  && pip install -r /tmp/requirements.txt