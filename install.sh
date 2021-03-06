#!/usr/bin/env bash

# Set up the management interface
# Needs some work, have just taken out of ansible playbook

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
MANAGER_DIR='/opt/metanyx/manager'

rm -rf ${MANAGER_DIR}.bak
cp -a ${MANAGER_DIR} ${MANAGER_DIR}.bak

# Create manager directory in /opt/metanyx
mkdir -p ${MANAGER_DIR}/{views,static}
chmod 0700 -R ${MANAGER_DIR}/

cd ${DIR}/src
cp bottle.py ${MANAGER_DIR}/
cp manage.py ${MANAGER_DIR}/
chmod 0600 ${MANAGER_DIR}/bottle.py
chmod 0700 ${MANAGER_DIR}/manage.py

cp init/metanyx-manager.service /etc/systemd/system/metanyx-manager
chmod 0600 /etc/systemd/system/metanyx-manager
cp init/metanyx-manager.sysvinit /etc/init.d/metanyx-manager
chmod 0700 /etc/init.d/metanyx-manager

cp views/* ${MANAGER_DIR}/views/
chmod 0600 ${MANAGER_DIR}/views/*
cp static/* ${MANAGER_DIR}/static/
chmod 0600 ${MANAGER_DIR}/static/*

systemctl enable metanyx-manager || update-rc.d metanyx-manager defaults

# Set ownership
# TODO: make this not root
chown -R root:root $MANAGER_DIR
