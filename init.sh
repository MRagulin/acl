#!/usr/bin/env bash
printf "Init deploying..."
mv /var/www/ACL /var/www/acl.vesta.ru -f
mkdir -p /var/www/acl.vesta.ru/log
chown -R www-data:www-data /var/www/acl.vesta.ru/log
cp /var/tmp/ACL.docx /var/www/acl.vesta.ru/templates/
chmod 777 /var/www/acl.vesta.ru/templates/ACL/docx
chmod 777 /var/www/acl.vesta.ru/static/docx
apt-get update
apt-get install libxslt-dev libxml2-dev libpam-dev libedit-dev
apt-get install python3-pip apache2 libapache2-mod-wsgi-py3


apt-get install postgresql
apt-get install python-psycopg2

sudo a2enmod wsgi

pip3 install Django==3.1.6
pip3 install psycopg2
pip3 install xlrd
pip3 install python-docx
pip3 install fontawesome-free==5.15.2
printf "Finish"
