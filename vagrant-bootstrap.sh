#!/usr/bin/env bash

mkdir /home/vagrant/bin
chown vagrant:vagrant /home/vagrant/bin
echo "PATH=$PATH:/home/vagrant/bin" >> /home/vagrant/.bashrc

###
#
# Don't install an SSH key. To use agent forwarding, just SSH in from putty.
#
###

echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA5Z143b4WtUCfZPhHb9LhexvtTNgyrT/8MBV9jboW27hBDN+3q1hG8VEgGCXCPj02xPIkEuiIv+9tYQQiWS4dMQ34yOYyuKBNn5gJKp79vwoH2GJp1upueXAUDhZYyXXXojZd4BIVf/pSlHQX88xRYp1/CRs2LqevimNB83zxjKLMfCQXTdTG9RM+JkAec3ugo9Q5zoyNhNUcdsFGRwWLdDd3kK3G6m5lWz0aahuqaLCIaSmN2w0oaKe9dTbArwoW6neCbyqlxCBGhgqM97FxNa8Wkz5z1zAwrT4uIVN6VUFm6Sf9JStYLONUpjKsKQSi0uDBOkf7ipTmFiI3I1xNAw== ipd21_leven" >> /home/vagrant/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA0mnTiF8Cdlem3ubrQiQ/sK0JJT33YsUZFhQE/YN3ami5j02hsHtSyEHB+sXqIv3b5bYafCVwBXuEnnJZwlVWfkDAI8GV+QUpPp1cU+cwY0aeAY35bkQLBvdbLvssaj1zQzvJehZXz1natm8wG2olCieePA66KyXt2Vjc1et6yzG0IQi7aV9UcHh1U8hf2QuT/ji3U869JUxIx0XY9gqYd2Wx1e/hnNdiXlQw5GCKO7hYizbkZnPVAFE5Xk6LpaWFlCG3baKXa+1FNXL+Ks75Q5nTzVNz/eAl/CiDvlAp51rf09eQ12GCiZ3lAuM4MaY7uOtmBF8y6/uiR3/BwLjIPQ== ipd21_home" >> /home/vagrant/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQB9dQWYzbYdTIFJfGgAUtxGFIlezY8gHgsdSc/f8ZNDWhYlowY9cRJEtkI9qLnUeJDoq9++qcO2rx2JFlRXrFGev+8S0hhWXMBqH34p4djSumBdoJw28LDePFvJqoqLNrxfnXCVYv+IW5KJcOD6DioZe2DL12CvWFssEctehWRwm30dNdpWHSPolHFoX75T7XaFJ0G9dc8UXQMdGNpeYurbjiFj+08KS03Qnsr/qNeYDYuHzJzHtfFs7ttoj4yqn1TNbygXSCraVHs9VqKjjH3eW9qiYSHGgKAKpO1L108eLJbyA+3edH9hw/kkG4gCjSBD0rFfIn8oB0/zrH/zFi0R ipd21_alpha" >> /home/vagrant/.ssh/authorized_keys

echo 'eval $(ssh-agent)' >> ~/.bashrc

apt-get update
apt-get -y install linux-image-extra-$(uname -r)
sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"
sh -c "echo deb http://get.docker.io/ubuntu docker main\ > /etc/apt/sources.list.d/docker.list"
apt-get update
apt-get -y install lxc-docker

usermod -a -G docker vagrant
