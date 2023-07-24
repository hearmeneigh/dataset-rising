#!/bin/sh -e

cd ./database
./stop-mongodb.sh
cd ..

docker rm e621-rising-mongo > /dev/null

