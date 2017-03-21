FROM ubuntu:latest
MAINTAINER E. Garcia "egaillera@gmail.com"

# Install required software
RUN apt-get update -y
RUN apt-get install -y python3-pip python3.5-dev build-essential

# Install cron to populate database
RUN apt-get install cron

# Install software
COPY . /meteo-aviso-be
WORKDIR /meteo-aviso-be
RUN pip3 install -r requirements.txt

RUN cp /meteo-aviso-be/etc/cronfile /etc/cron.d/simple-cron

# Create logs directory
WORKDIR /meteo-aviso-be/app
RUN mkdir logs

# Start server
ENTRYPOINT ["python3"]
CMD ["main.py"]
