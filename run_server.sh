#!/bin/bash
set -e  # Exit on error

# Inputs
git_repo_url="$2"
branch="$3"

# Activate environment
source /env/bin/activate

# Clone the repo into a subfolder
echo "Cloning $git_repo_url (branch: $branch)"
git clone -b "$branch" "$git_repo_url" code

# Run app
echo "$PWD"
ls

echo "cd to code"
cd "code"|| exit
ls

echo "Running the application..."
export FLASK_DEBUG=1
flask run -h 0.0.0.0 -p 80
