#!/usr/bin/env bash
printf "Init deploying..."
mkdir -p /var/www/acladmin/log
apt-get update
apt-get install libxslt-dev libxml2-dev libpam-dev libedit-dev
apt-get install python3-pip apache2 libapache2-mod-wsgi-py3
sudo a2enmod wsgi

#apt-get install -y libapache2-mod-wsgi-py3
apt-get install postgresql
apt-get install python-psycopg2

pip3 install psycopg2
pip3 install Django==3.1.6
pip3 install python-docx
pip3 install fontawesome-free
pip3 install xlrd
printf "Finish"
