# Function to validate errors
function valid () {
  if [ $1 -eq 0 ]; then
      echo Done
  else
      echo Error!!
      exit 1
  fi
}

# Stop running containers
echo "Stopping containers ..."
sudo docker-compose -f meteo-aviso-be/docker-compose-rpi.yaml down
valid $?

# Remove old image
echo "Removing old meteo-aviso-be image ..."
sudo docker rmi meteo-aviso-be
valid $?

# Remove old software and download new one
echo "Installing new software ..."
rm -rf meteo-aviso-be.old
mv meteo-aviso-be meteo-aviso-be.old
git clone https://github.com/egaillera/meteo-aviso-be

# Build new image
echo "Building new image ..."
sudo docker build -t meteo-aviso-be:latest -f meteo-aviso-be/Dockerfile.rpi meteo-aviso-be
valid $?

# Start containers
echo "Starting containers ..."
docker-compose -f meteo-aviso-be/docker-compose-rpi.yaml up -d
valid $?

# Copy certificate to send notifications
echo "Copying .pem file ..."
sudo docker cp MeteoAvisoPushCert.pem meteo-aviso-cl:/home/meteo/meteo-aviso-be/app/scripts/.
valid $?

