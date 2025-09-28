#!/bin/bash
# run.sh

# Fail on errors
set -e

# Initialize database (drop and recreate if needed)
export FLASK_APP=server.py
flask init-db --drop

# Start the Flask server
python server.py
