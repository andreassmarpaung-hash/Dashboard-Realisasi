#!/bin/bash

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run dashboard
echo "🚀 Starting Dashboard..."
streamlit run dashboard.py
