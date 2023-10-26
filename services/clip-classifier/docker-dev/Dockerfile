# syntax=docker/dockerfile:1
   
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

RUN apt-get update && apt-get install -y git

WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt

RUN python -c "import clip; clip.load('ViT-B/32', download_root='/app/clip-data/CLIP')"