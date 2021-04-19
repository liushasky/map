FROM gboeing/osmnx
LABEL maintainer="zjia@ksmconsulting.com"

USER root
RUN apt-get update && apt-get install -y unzip git vim

USER $NB_UID

# pip install
COPY requirements.txt /scripts/requirements.txt
RUN pip install -r /scripts/requirements.txt

COPY utils.py /scripts/utils.py
COPY data.py /scripts/data.py

# will be overwritten by kf pipeline
ENTRYPOINT [ "python", "/scripts/data.py" ]
