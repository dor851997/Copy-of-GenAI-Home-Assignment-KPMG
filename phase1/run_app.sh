#!/bin/bash

# Activate your Python virtual environment
source ../venv/bin/activate

# Start Celery in the background
celery -A analyze.celery_app worker --loglevel=info &

# Start the Streamlit app
streamlit run app.py

# Optional: Deactivate environment after closing
# deactivate
