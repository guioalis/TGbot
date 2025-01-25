#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements-vercel.txt

echo "Checking installations..."
pip list

echo "Python version:"
python --version 