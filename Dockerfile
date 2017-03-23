FROM python:3.5

MAINTAINER E. Garcia "egaillera@gmail.com"

RUN groupadd -r meteo && useradd -r -g meteo meteo

# Install software
COPY . /meteo-aviso-be
WORKDIR /meteo-aviso-be
RUN pip3 install -r requirements.txt

# Create logs directory
WORKDIR /meteo-aviso-be/app
RUN mkdir logs

# Start server
#ENTRYPOINT ["python3"]
#CMD ["main.py"]
CMD ["/usr/local/bin/uwsgi", "--http", "0.0.0.0:9090", "--wsgi-file", "/meteo-aviso-be/app/main.py","--callable", "app", "--stats", "0.0.0.0:9091"]
