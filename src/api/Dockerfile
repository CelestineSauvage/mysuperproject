# Image python
FROM python:3.12-slim

# create workdir
WORKDIR /code

# copy requirements.txt specific to our fast-api app
COPY src/api/requirements.txt /code/requirements.txt

# Install all necessary python packages
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy dir
COPY src/api /code/api
COPY src/helpers /code/helpers

# Port 8000
EXPOSE 8000

ENV MONGO_ADMIN=admin
ENV MONGO_ADMIN_PASS=pass

# Command to run
CMD ["uvicorn", "api.MongoDBAPI:app", "--host", "0.0.0.0", "--port", "8000"]