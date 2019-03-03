#!/usr/bin/env bash

# Abort script at first error, when a command exits with non-zero status
set -e

# Set working directory to location of the script to prevent disasters
cd $(dirname $0)
basedir=$(pwd)

# Create and activate a virtual Python environment
virtualenv -p python3 chaos-build-env
source chaos-build-env/bin/activate

# Install dependencies via Poetry
poetry install

cd chaos

# Create the executable with Pyinstaller
pyinstaller --noconfirm \
    --onedir \
    --noupx \
    --strip \
    --log-level=INFO \
    chaosd.py

# Get out of the virtual environment
deactivate

# Rearrangement and cleanup of files and directories
cleanup () {
    rm -rf chaos \
        chaos-build-env \
        chaos.egg-info \
        pip-wheel-metadata
    mv chaosd chaos
    find . -maxdepth 1 -type f ! -name 'build.sh' -exec rm -f {} +
    rm build.sh
}

cd dist
mv chaosd ../..
cd ../..

if [[ $(pwd) -ef "$basedir" ]]; then
    cleanup
else
    exit 1
fi