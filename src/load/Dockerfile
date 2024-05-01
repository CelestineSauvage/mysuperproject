FROM python:3.12-slim


COPY src/load/requirements.txt project/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /project/requirements.txt

COPY src/load_data_into_db.py project/load_data_into_db.py
COPY src/load/DataInsertion.py project/load/DataInsertion.py
COPY src/helpers project/helpers

WORKDIR project
RUN mkdir logs

ENV DOWNLOAD_FOLDER=downloads

CMD python3 load_data_into_db.py --path $DOWNLOAD_FOLDER
