#!/usr/bin/env bash

apt-get update
apt-get -y install linux-image-extra-$(uname -r)
sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"
sh -c "echo deb http://get.docker.io/ubuntu docker main\ > /etc/apt/sources.list.d/docker.list"
apt-get update
apt-get -y install lxc-docker

usermod -a -G docker vagrant
