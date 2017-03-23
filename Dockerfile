FROM python:3.5

MAINTAINER E. Garcia "egaillera@gmail.com"

RUN groupadd -r meteo && useradd -r -g meteo meteo
USER meteo

# Install software
COPY . /home/meteo/meteo-aviso-be
WORKDIR /home/meteo/meteo-aviso-be
USER root
RUN pip3 install -r requirements.txt

# Create logs directory
WORKDIR /home/meteo/meteo-aviso-be/app
USER meteo
RUN mkdir logs

# Start server
CMD ["/usr/local/bin/uwsgi", "--http", "0.0.0.0:9090", "--wsgi-file", "/meteo-aviso-be/app/main.py","--callable", "app", "--stats", "0.0.0.0:9091"]
