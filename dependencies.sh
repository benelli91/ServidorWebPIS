#!/bin/bash
#DJANGO
pip install django psycopg2

#SELENIUM
pip install selenium
## MODULO-unidecode
sudo pip install unidecode
#DRIVER FIREFOX
cd ~
export GECKODRIVER="geckodriver-v0.16.1-linux64"
sudo wget https://github.com/mozilla/geckodriver/releases/download/v0.16.1/$GECKODRIVER.tar.gz
sudo tar -xvzf $GECKODRIVER.tar.gz
sudo mv geckodriver /usr/local/share
sudo ln -sf /usr/local/share/geckodriver /usr/local/bin
sudo chmod +x /usr/local/bin/geckodriver
##display para que ande firefox en servidor
sudo apt-get install xvfb
sudo pip install pyvirtualdisplay

#API DJANGO!  ----> in settings.py, on installed apps, add: 'rest_framework'
sudo pip install djangorestframework


#Otros
sudo pip install beautifulsoup4
sudo pip install requests
sudo pip install lxml
sudo pip install ipdb
