#!/bin/bash

# Activate your virtual environment
source ../venv/bin/activate

# Run the FastAPI backend server
(cd backend && uvicorn main:app --reload) &

# Run the Streamlit frontend app
(cd frontend && streamlit run app.py) &

wait