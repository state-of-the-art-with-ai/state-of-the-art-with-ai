#!/bin/bash

set -e 

sota container_startup setup
(sota scheduler run_scheduler 2>&1 | tee -a /tmp/scheduler.log) &
streamlit run --server.address '0.0.0.0' --server.port '80' state_of_the_art/app/start.py