FROM python:3.6
LABEL maintainer="jon.duckworth@digitalglobe.com"

# Install the C compiler tools
RUN apt-get update -y && \
  apt-get install build-essential -y && \
  pip install --upgrade pip

# Install libspatialindex
WORKDIR /tmp
RUN wget http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz && \
  tar -xvzf spatialindex-src-1.8.5.tar.gz && \
  cd spatialindex-src-1.8.5 && \
  ./configure && \
  make && \
  make install && \
  cd - && \
  rm -rf spatialindex-src-1.8.5* && \
  ldconfig

# pip install
COPY requirements.txt /scripts/requirements.txt
RUN pip install -r /scripts/requirements.txt

COPY utils.py /scripts/utils.py
COPY data.py /scripts/data.py

# will be overwritten by kf pipeline
ENTRYPOINT [ "python", "/scripts/data.py" ]