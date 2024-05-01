FROM python:3.12-slim

COPY requirements.txt project/requirements.txt
RUN --mount=type=cache,target=/var/cache/pip3 \
    pip3 install -r project/requirements.txt

COPY src/data_transform.py project/data_transform.py
COPY src/transform project/transform
COPY src/helpers project/helpers

WORKDIR project
RUN mkdir logs

ENV DOWNLOAD_FOLDER=downloads/FT
ENV SOURCE=0

CMD python3 data_transform.py $DOWNLOAD_FOLDER $SOURCE
