#!/bin/sh -ex

if [ -z "${DB_USERNAME}" ]
then
  DB_USERNAME='root'
fi

if [ -z "${DB_PASSWORD}" ]
then
  DB_PASSWORD='root'
fi

docker start e621-rising-mongo &> /dev/null || docker run --name e621-rising-mongo -e "MONGO_INITDB_ROOT_USERNAME=${DB_USERNAME}" -e "MONGO_INITDB_ROOT_PASSWORD=${DB_PASSWORD}" -p 27017:27017 -d mongo:6 > /dev/null
