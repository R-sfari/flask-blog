#!/bin/bash

set -e

echo -e "Running $FLASK_CONFIG Configuration\n"

if [ "$FLASK_CONFIG" = "DEV" ]; then
  echo -e "Running Development Server\n************\n"
  exec python3 /blog/uwsgi.py

elif [ "$FLASK_CONFIG" = "TEST" ]; then
  echo -e "Running Unit Test\n***********\n"
  exec flask run-tests

else
  echo -e "Running Production Server\n*************"
  exec uwsgi --ini /blog/uwsgi.ini
fi
