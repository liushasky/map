FROM python:3.7
LABEL maintainer="zjia@ksmconsulting.com"

# Install the C compiler tools
RUN apt-get update -y && \
  apt-get install build-essential -y && \
  pip install --upgrade pip

# pip install
COPY requirements.txt /scripts/requirements.txt
RUN pip install -r /scripts/requirements.txt

COPY data.py /scripts/data.py

# will be overwritten by kf pipeline
ENTRYPOINT [ "python", "/scripts/data.py" ]