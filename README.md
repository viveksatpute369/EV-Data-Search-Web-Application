# Project Setup and Virtual Environment

This README provides instructions for setting up a Python virtual environment (venv) and running a Streamlit project. It ensures that all dependencies are isolated and provides guidance on using Streamlit.

## Prerequisites

- **Python**: Ensure Python is installed on your system. You can download it from the [Python website](https://www.python.org/downloads/).

## Step-by-Step Guide

# before you run main.py you have to download llama2 model from ollama then it will work else not.

### 1. Create the Virtual Environment

python -m venv env

2. Activate the Virtual Environment

On Windows:

env\Scripts\activate

On macOS/Linux:

source env/bin/activate

3. Install Required Dependencies

pip install streamlit pandas matplotlib pydeck langchain

4. Running Your Project

streamlit run your_script.py

it will be start default running on 

http://localhost:8501
