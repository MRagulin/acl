#!/usr/bin/env bash
mkdir -p /var/www/ACL/log
apt-get update
sudo apt-get install postgresql
sudo apt-get install python-psycopg2
apt-get install libxslt-dev libxml2-dev libpam-dev libedit-dev
pip install psycopg2


