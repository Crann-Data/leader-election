#!/bin/bash
trap 'kill 0' SIGINT

# running scripts
python src/main.py 5000 &
python src/main.py 5001 &
python src/main.py 5002 &
wait
