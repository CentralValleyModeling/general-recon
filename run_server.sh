#!/bin/bash

# Activate environment
source /env/bin/activate

git_repo_url="https://github.com/CentralValleyModeling/calsim-dash.git"

# Clone the repo into a subfolder
echo "cloning repo $1"
git clone -b production "$git_repo_url"

# Run app
echo "$PWD"
ls

echo "cd to calsim-dash"
cd "calsim-dash"
ls

echo "Running the application..."
flask run -h 0.0.0.0 -p 80