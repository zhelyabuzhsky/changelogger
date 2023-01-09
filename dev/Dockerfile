FROM python:3.11-alpine  AS development_build

RUN apk add --no-cache make

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .