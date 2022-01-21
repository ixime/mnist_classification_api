name: Tests

on:
  push:
    branches:
      - main

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python 3.8
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        python3 -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Linting
      run: |
        flake8
    - name: Coverage report and testing
      run: |
        pip install coverage
        coverage run manage.py test
        coverage report
