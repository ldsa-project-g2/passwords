#!/bin/sh
#apt-get --yes update
#apt-get install --yes software-properties-common
sudo apt-add-repository --yes ppa:ansible/ansible
sudo apt-get --yes update
sudo apt-get install --yes ansible
