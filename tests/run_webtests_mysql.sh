#!/bin/bash

# install google chrome 133.0.6943.141
wget -P /tmp http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_133.0.6943.141-1_amd64.deb
dpkg --force-all -i /tmp/google-chrome-stable_133.0.6943.141-1_amd64.deb || true
apt-get update -qqq
apt-get install -f -y -qqq

google-chrome --version

pip install .
pip install -r tests/requirements.txt

export PYTHONPATH=$(pwd)
export ZOOM_TEST_DATABASE_HOST=mysql
export ZOOM_TEST_DATABASE_USER=root
export ZOOM_TEST_DATABASE_PASSWORD=root
export ZOOM_DEFAULT_INSTANCE=$(pwd)/zoom/_assets/web
export ZOOM_DEFAULT_SITE_INI=$ZOOM_DEFAULT_INSTANCE/sites/localhost/site.ini
export ZOOM_TEST_LOG=$ZOOM_DEFAULT_INSTANCE

zoom database \
    -e mysql \
    -H $ZOOM_TEST_DATABASE_HOST \
    -u $ZOOM_TEST_DATABASE_USER \
    -p $ZOOM_TEST_DATABASE_PASSWORD \
    create zoomdata

zoom database \
    -e mysql \
    -H $ZOOM_TEST_DATABASE_HOST \
    -u $ZOOM_TEST_DATABASE_USER \
    -p $ZOOM_TEST_DATABASE_PASSWORD \
    create zoomtest


cat <<EOL >> $ZOOM_DEFAULT_SITE_INI
host=$ZOOM_TEST_DATABASE_HOST
user=$ZOOM_TEST_DATABASE_USER
password=$ZOOM_TEST_DATABASE_PASSWORD
EOL

# set display port to avoid crash
export DISPLAY=:99

# get locales not included in base Python image
apt-get update && apt-get install -y --no-install-recommends \
    locales \
    locales-all

# set locale
export LC_ALL=C

# run zoom server
zoom serve -p 8000 $ZOOM_DEFAULT_INSTANCE &

cat $ZOOM_DEFAULT_SITE_INI

pytest tests/apptests
pytest tests/webtests

