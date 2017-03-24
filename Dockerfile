FROM python:3.5

MAINTAINER E. Garcia "egaillera@gmail.com"

RUN groupadd -r meteo && useradd -r -g meteo meteo

# Install software
COPY . /home/meteo/meteo-aviso-be
WORKDIR /home/meteo/meteo-aviso-be
RUN pip3 install -r requirements.txt
RUN chown -R meteo:meteo /home/meteo/meteo-aviso-be 

# Create logs directory
USER meteo
RUN mkdir /home/meteo/meteo-aviso-be/app/logs

# Start server
#CMD ["/usr/local/bin/uwsgi", "--http", "0.0.0.0:9090", "--wsgi-file", "/home/meteo/meteo-aviso-be/app/main.py","--callable", "app", "--stats", "0.0.0.0:9091"]
RUN chmod +x start.sh
CMD ["./start.sh"] 
