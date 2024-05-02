# Image python
FROM python:3.12-slim

# create workdir


# copy requirements.txt specific to our fast-api app
COPY src/addcollection/requirements.txt /code/requirements.txt

# Install all necessary python packages
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy dir
COPY src/addcollection /code/addcollection
COPY src/helpers /code/helpers

WORKDIR /code

ENV PYTHONPATH "${PYTHONPATH}:/code/helpers"
ENV MONGO_HOST=localhost
ENV MONGO_ADMIN=admin
ENV MONGO_ADMIN_PASS=pass

# Command to run
CMD ["python3", "addcollection/load_annex_into_db.py"]