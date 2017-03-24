#!/bin/bash 

set -e 

if [ "$ENV" = 'COLLECTION' ]; then 
	while true 
	do 
	   echo "Running Collection Daemon"
	   exec python "/home/meteo/meteo-aviso-be/app/scripts/get_mc_data.py" 
	   sleep 900
	done
	
else 
	echo "Running Application Server" 
	exec uwsgi --http 0.0.0.0:9090 --wsgi-file /home/meteo/meteo-aviso-be/app/main.py --callable app --stats 0.0.0.0:9191 
fi
