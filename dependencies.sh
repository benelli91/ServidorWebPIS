#!/bin/bash

#SELENIUM!
##PRIMER MODULO
sudo apt-get update
sudo apt-get install build-essential chrpath libssl-dev libxft-dev -y
sudo apt-get install libfreetype6 libfreetype6-dev -y
sudo apt-get install libfontconfig1 libfontconfig1-dev -y
cd ~
export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
sudo wget https://github.com/Medium/phantomjs/releases/download/v2.1.1/$PHANTOM_JS.tar.bz2
sudo tar xvjf $PHANTOM_JS.tar.bz2
sudo mv $PHANTOM_JS /usr/local/share
sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
phantomjs --version
##SEGUNDO MODULO
sudo pip install unidecode

#API DJANGO!
sudo pip install djangorestframework

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
##
sudo pip install requests
