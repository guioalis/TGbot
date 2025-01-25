#!/bin/bash
set -e

echo "Python version:"
python --version

echo "Pip version:"
pip --version

echo "Creating .pip directory..."
mkdir -p .pip

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies to .pip directory..."
pip install -r requirements-vercel.txt --target .pip

echo "Installed packages:"
pip list

echo "Directory contents:"
ls -la

echo "Pip directory contents:"
ls -la .pip 