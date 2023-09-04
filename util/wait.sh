#!/bin/bash

if [ -z "${1}" ]
then
  echo "Usage: wait.sh PID"
  exit 1
fi

tail --pid=$1 -f /dev/null

