FROM ubuntu:latest
MAINTAINER E. Garcia "egaillera@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /meteo-aviso-be
WORKDIR /meteo-aviso-be
RUN pip install -r requirements.txt
WORKDIR /meteo-aviso-be/app
ENTRYPOINT ["python"]
CMD ["main.py"]
