# syntax=docker/dockerfile:1
   
FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y git

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt