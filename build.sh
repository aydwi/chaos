#!/usr/bin/env bash

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
cd dist
mv chaosd ../..
cd ../..
rm -rf chaos \
    chaos-build-env \
    chaos.egg-info \
    pip-wheel-metadata
mv chaosd chaos
find . -maxdepth 1 -type f ! -name 'build.sh' -exec rm -f {} +
rm build.sh
