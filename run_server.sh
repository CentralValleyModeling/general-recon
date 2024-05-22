#!/bin/bash

# Activate environment
source /env/bin/activate

git_repo_url="https://github.com/CentralValleyModeling/calsim-dash.git"

# Clone the repo into a subfolder
echo "cloning repo $1"
git clone -b production "$git_repo_url" "code"

# Run app
echo "Running the application..."

flask run --host 0.0.0.0 --port 80