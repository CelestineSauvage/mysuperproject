FROM python:3.12-slim

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update \
    && apt-get install -y wget \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb

COPY src/extract/requirements.txt project/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /project/requirements.txt

COPY src/data_download.py project/data_download.py
COPY src/extract project/extract
COPY src/helpers project/helpers

WORKDIR project
RUN mkdir logs

ENV DOWNLOAD_FOLDER=downloads/FT
ENV SOURCE=0
ENV PUBLIEEDEPUIS=1
ENV ADDITIONAL_ARGUMENT=

CMD python3 data_download.py --path $DOWNLOAD_FOLDER --source $SOURCE --publieeDepuis $PUBLIEEDEPUIS $ADDITIONAL_ARGUMENT
