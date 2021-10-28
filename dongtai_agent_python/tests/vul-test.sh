#!/bin/bash

HOST=$1

if [ -z ${HOST} ]; then
  echo -e "api host required!"
  echo -e "Usage: $( basename $0 ) <api host>"
  exit 1
fi

curl "${HOST}/get_open?name=Data"
