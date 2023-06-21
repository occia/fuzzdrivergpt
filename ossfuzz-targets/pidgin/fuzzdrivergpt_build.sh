#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang
export MAKEFLAGS="-j`nproc`"
set -eux
# FILL HERE
apt remove -y automake
mkdir /src/automake
cd /src/automake
wget https://mirrors.tuna.tsinghua.edu.cn/gnu/automake/automake-1.16.3.tar.gz
tar xvf automake-1.16.3.tar.gz
cd automake-1.16.3
./configure
make -j$(nproc) install
ln -s /usr/local/bin/automake  /usr/bin/automake
export ACLOCAL_PATH=/usr/share/aclocal
apt install -y intltool


cat >> /src/build.sh << 'EOF'

cd /src/pidgin
make clean
./configure --disable-consoleui \
            --disable-shared \
            --disable-screensaver \
            --disable-sm \
            --disable-gtkspell \
            --disable-gevolution \
            --enable-gnutls=no \
            --disable-gstreamer \
            --disable-vv \
            --disable-idn \
            --disable-meanwhile \
            --disable-avahi \
            --disable-dbus \
            --disable-perl \
            --disable-tcl \
            --disable-cyrus-sasl \
            --disable-gtkui \
            --enable-nss=no --prefix=/src/pidgin/fuzzdrivergpt-install
make -j$(nproc) install

EOF
set +eux

#
# do what should be done in build_fuzzers command
#
compile
#
#
#

##########
## After compile, you can prepare the include/lib staff here
##########

set -eux

##########
# UNCOMMENT this for manual exploration on how to write this fuzzdrivergpt_build.sh
# COMMENT this for testing the real logic of fuzzdrivergpt_build.sh
##########
#while true
#do
#	sleep 1h
#done
#

INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/pidgin/fuzzdrivergpt-install/include ${INSTALL}/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/pidgin/fuzzdrivergpt-install/lib ${INSTALL}/lib
