FROM python:3.12-slim

COPY requirements.txt project/requirements.txt
RUN --mount=type=cache,target=/var/cache/pip3 \
    pip3 install -r project/requirements.txt

COPY src/load_data_into_db.py project/load_data_into_db.py
COPY src/load/DataInsertion.py project/load/DataInsertion.py
COPY src/helpers project/helpers

WORKDIR project
RUN mkdir logs

ENV DOWNLOAD_FOLDER=downloads

CMD python3 load_data_into_db.py $DOWNLOAD_FOLDER
