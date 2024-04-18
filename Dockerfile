FROM python:3.10.12

WORKDIR /home

ADD requirements.txt /home/bot/
WORKDIR /home/bot

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ADD ./dicks /home/bot/dicks
ADD ./models /home/bot/models
ADD ./app /home/bot/app

ENV PYTHONPATH=$PYTHONPATH:/home/bot/app
CMD python app/main.py