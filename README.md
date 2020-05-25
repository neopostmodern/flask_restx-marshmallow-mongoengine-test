# Backend Prototype Flask

## Getting started
Execute these scripts / commands in the same terminal (to preserve venv)
1. `setup.sh` (creates venv and installs dependencies)
2. `mongo.sh` (start mongo instance from docker image)
3. `python app.py` 

## Issues found with this approach
- [flask_accepts can't handle different status codes per route properly](https://github.com/apryor6/flask_accepts/issues/17) 
  (and silently suppresses them)