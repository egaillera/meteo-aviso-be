FROM ubuntu:latest
MAINTAINER E. Garcia "egaillera@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3.5-dev build-essential
COPY . /meteo-aviso-be
WORKDIR /meteo-aviso-be
RUN pip3 install -r requirements.txt
WORKDIR /meteo-aviso-be/app
ENTRYPOINT ["python3"]
CMD ["main.py"]
