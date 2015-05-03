#!/usr/bin/env bash

# Set up the management interface
# Needs some work, have just taken out of ansible playbook

MANAGER_DIR='/opt/metanyx/manager/'

# Create manager directory in /opt/metanyx
mkdir -m 0700 -p ${MANAGER_DIR}{views,static}

cd src
cp bottle.py ${MANAGER_DIR}
cp manage.py ${MANAGER_DIR}
chmod 0600 ${MANAGER_DIR}bottle.py
chmod 0700 ${MANAGER_DIR}manage.py

cp metanyx-manager.service /etc/systemd/system/metanyx-manager
chmod 0600 /etc/systemd/system/metanyx-manager
cp metanyx-manager.sysvinit /etc/init.d/metanyx-manager
chmod 0700 /etc/init.d/metanyx-manager
cp setup_template.tpl ${MANAGER_DIR}views/
cp status_template.tpl ${MANAGER_DIR}views/
chmod 0600 ${MANAGER_DIR}views/*
cp style.css ${MANAGER_DIR}static/
chmod 0600 ${MANAGER_DIR}static/*

systemctl enable metanyx-manager || update-rc.d metanyx-manager defaults

# Set ownership
# TODO: make this not root
chown -R root:root $MANAGER_DIR
