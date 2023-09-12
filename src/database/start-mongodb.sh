#!/bin/sh -ex

if [ -z "${DB_USERNAME}" ]
then
  DB_USERNAME='root'
fi

if [ -z "${DB_PASSWORD}" ]
then
  DB_PASSWORD='root'
fi

if [ -z "${DB_PORT}" ]
then
  DB_PORT=27017
fi

docker start e621-rising-mongo || docker run --name e621-rising-mongo --restart always -e "MONGO_INITDB_ROOT_USERNAME=${DB_USERNAME}" -e "MONGO_INITDB_ROOT_PASSWORD=${DB_PASSWORD}" -p "${DB_PORT}:${DB_PORT}" -d mongo:6
