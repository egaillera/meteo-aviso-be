FROM egaillera/meteo-aviso-base:latest

MAINTAINER E. Garcia "egaillera@gmail.com"

# Install project software
COPY . /home/meteo/meteo-aviso-be
WORKDIR /home/meteo/meteo-aviso-be
RUN chown -R meteo:meteo /home/meteo/meteo-aviso-be 

# Create folder to share data and to create the socket
RUN mkdir /shared_data
RUN chown -R meteo:meteo /shared_data

# Create logs directory
USER meteo
RUN mkdir -p /home/meteo/meteo-aviso-be/app/logs

# Start server
RUN chmod +x start.sh
WORKDIR /home/meteo/meteo-aviso-be/app
CMD ["../start.sh"] 
