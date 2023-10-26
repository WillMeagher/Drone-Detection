# syntax=docker/dockerfile:1
   
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git libgl1 libglib2.0-0

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt