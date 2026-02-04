FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs \
  && npm install -g npm

COPY containers/requirements.txt /tmp/requirements.txt
WORKDIR /root/workspace

RUN pip install --upgrade pip setuptools \
  && pip install -r /tmp/requirements.txt

WORKDIR /root/workspace/src/sample