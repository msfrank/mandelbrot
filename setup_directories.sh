#!/bin/bash

# ask for virtualenv root
read -p "Please tell me where your virtualenv is located: " VENV
#parent directory
parent_directory="$(readlink -f "$VENV")"

# make etc folder
echo "creating etc folder in $parent_directory/etc"
mkdir -p $parent_directory/etc
echo "Making mandelbrot aware of $parent_directory/etc"
python setup.py pesky_default --command set --key SYSCONF_DIR --value "$parent_directory/etc"

echo "creating var/lib/systems folder in $parent_directory/var/lib/systems"
echo "creating var/lib/agent folder in $parent_directory/var/lib/agent"
mkdir -p $parent_directory/var/lib/agent "$parent_directory/var/lib/systems"
echo "Making mandelbrot aware of $parent_directory/var/lib"
python setup.py pesky_default --command set --key LOCALSTATE_DIR --value "$parent_directory/var/lib"

echo "creating var/run folder in $parent_directory/var/run"
mkdir -p $parent_directory/var/run/
echo "Making mandelbrot aware of $parent_directory/var/run"
python setup.py pesky_default --command set --key RUN_DIR --value "$parent_directory/var/run"

# create sample configs
cp doc/mandelbrot.conf.example "$parent_directory/etc/mandelbrot.conf"
cp doc/system.yaml.example "$parent_directory/var/lib/systems/system.yaml"
