FROM python:3.9

WORKDIR /app
COPY . .
WORKDIR /app/marketer_space
COPY ./requirements.txt .

RUN pip install -r requirements.txt
