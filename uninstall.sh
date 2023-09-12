#!/bin/sh -e

cd ./database
./stop-mongodb.sh
cd ..

docker rm e621-rising-mongo || echo 'no instance to remove' > /dev/null
