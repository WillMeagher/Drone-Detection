# syntax=docker/dockerfile:1
   
FROM python:3.10-slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git ffmpeg libsm6 libxext6 libgl1 libglib2.0-0 procps

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt