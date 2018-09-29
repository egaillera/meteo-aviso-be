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
echo "Stopping web server ..."
sudo systemctl stop docker-meteoaviso_be
valid $?
echo "Stopping collector ..."
sudo systemctl stop docker-meteoaviso_cl
valid $?

# Remove old image
echo "Removing old meteo-aviso-be image ..."
docker rmi meteo-aviso-be
valid $?

# Build new image
echo "Building new image ..."
docker build -t meteo-aviso-be:latest github.com/egaillera/meteo-aviso-be
valid $?

# Start containers
echo "Starting web server ..."
sudo systemctl start docker-meteoaviso_be
valid $?
echo "Starting collector ..."
sudo systemctl start docker-meteoaviso_cl
valid $?

# Copy certificate to send notifications
echo "Copying .pem file ..."
docker cp MeteoAvisoPushCert.pem meteo-aviso-collector:/home/meteo/meteo-aviso-be/app/scripts/.
valid $?

# Remove unused containers
echo "Deleting unused containers ..."
docker rm $(docker ps -qa --no-trunc --filter "status=exited")
valid $?
