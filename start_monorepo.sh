#!/bin/bash

set -e 

# downloads assets
sota container_startup setup

echo "Starting scheduler"
PYTHONUNBUFFERED=TRUE sota scheduler run | tee /tmp/scheduler.log &

streamlit run --server.address '0.0.0.0' --server.port '80' --global.developmentMode False --global.suppressDeprecationWarnings True state_of_the_art/app/start.py
