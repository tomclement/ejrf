#!/bin/sh
source ../ejrf_env/bin/activate
cp eJRF/snap-ci/snap-settings.py eJRF/localsettings.py
./manage.py harvest
coveralls