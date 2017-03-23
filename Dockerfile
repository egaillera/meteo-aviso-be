FROM python:3.5

MAINTAINER E. Garcia "egaillera@gmail.com"

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
CMD ["uwsgi", "--http", "0.0.0.0:5000", "--wsgi-file", "/meteo-aviso-be/app/main.py", \ "--callable", "app", "--stats", "0.0.0.0:5001"]
