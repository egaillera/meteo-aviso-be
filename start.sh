#!/bin/bash 

set -e 

if [ "$ENV" = 'COLLECTOR' ]; then 
	while true 
	do 
	   echo "Running Collection Daemon"
	   python "/home/meteo/meteo-aviso-be/app/scripts/collect_data.py" 
	   sleep 900
	done
	
else 
	echo "Running Application Server" 
	exec uwsgi --http 0.0.0.0:9090 --wsgi-file /home/meteo/meteo-aviso-be/app/main.py --callable app --stats 0.0.0.0:9091 
fi
