# syntax=docker/dockerfile:1
   
FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y git libgl1 libglib2.0-0 procps

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt