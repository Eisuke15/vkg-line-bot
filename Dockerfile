FROM python:3.8
ADD requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt
