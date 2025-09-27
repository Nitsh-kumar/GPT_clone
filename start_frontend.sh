#!/bin/bash
echo "Starting Streamlit Frontend..."
cd frontend
pip install -r ../Requirement.txt
streamlit run main.py --server.port 8501