FROM jupyter/base-notebook
LABEL maintainer="Geoff Boeing <boeing@usc.edu>"
LABEL url="https://github.com/gboeing/osmnx"
LABEL description="OSMnx is a Python package to retrieve, model, analyze, and visualize OpenStreetMap networks and other spatial data."

USER root
RUN apt-get update && apt-get install -y unzip git vim ca-certificates curl apt-transport-https lsb-release gnupg

USER $NB_UID
COPY requirements.txt /tmp/

RUN conda install -c conda-forge openpyxl scikit-learn seaborn kubernetes kfp && conda clean --all --yes

# configure conda and install packages in one RUN to keep image tidy
RUN conda config --set show_channel_urls true && \
    conda config --set channel_priority strict && \
    conda config --prepend channels conda-forge && \
    conda update --yes -n base conda && \
    conda install --update-all --force-reinstall --yes --file /tmp/requirements.txt && \
    rm -f -r -v /opt/conda/share/jupyter/kernels/python3 && \
    python -m ipykernel install --sys-prefix --name ox --display-name "Python (ox)" && \
    conda clean --all --yes && \
    conda info --all && \
    conda list && \
    jupyter kernelspec list && \
    ipython -c "import osmnx; print('OSMnx version', osmnx.__version__)"

RUN pip install mapboxgl mapbox mapboxgl_notebook

COPY merge.py /scripts/merge.py
COPY geometry_join.py /scripts/geometry_join.py

# will be overwritten by kf pipeline
ENTRYPOINT [ "python", "/scripts/merge.py" ]