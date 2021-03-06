#!/bin/bash

pip install .
pip install -r tests/requirements.txt

export PYTHONPATH=$(pwd)

zoom database -e mysql -H mariadb -u root -p root create zoomdata
zoom database -e mysql -H mariadb -u root -p root create zoomtest

export ZOOM_TEST_DATABASE_HOST=mariadb
export ZOOM_TEST_DATABASE_USER=root
export ZOOM_TEST_DATABASE_PASSWORD=root

export ZOOM_DEFAULT_INSTANCE=$(pwd)/zoom/_assets/web
export ZOOM_DEFAULT_SITE_INI=$ZOOM_DEFAULT_INSTANCE/sites/localhost/site.ini

echo "host=mariadb" >> $ZOOM_DEFAULT_SITE_INI
echo "user=root" >> $ZOOM_DEFAULT_SITE_INI
echo "password=root" >> $ZOOM_DEFAULT_SITE_INI

# install google chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get -y update
apt-get install -y google-chrome-stable

# install chromedriver
apt-get install -yqq unzip
wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

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

nosetests --with-doctest --with-coverage --cover-package=zoom -vx zoom tests/unittests tests/apptests tests/webtests --exclude-dir=zoom/testing --exclude-dir=zoom/cli
