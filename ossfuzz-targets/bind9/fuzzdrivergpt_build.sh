#!/bin/bash

##########
# UNCOMMENT this for manual exploration on how to write this fuzzdrivergpt_build.sh
# COMMENT this for testing the real logic of fuzzdrivergpt_build.sh
##########
#while true
#do
#	sleep 1h
#done

##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang

set -eux
# FILL HERE
cat >> /src/build.sh << 'EOF'
cd /src/bind9
make clean
./configure --disable-shared --enable-static --enable-developer --without-cmocka --without-zlib --prefix=/src/bind9/fuzzdrivergpt-install
make install

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

INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
#while true
#do
#	sleep 1h
#done
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/bind9/fuzzdrivergpt-install/include ${INSTALL}/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/bind9/fuzzdrivergpt-install/lib ${INSTALL}/lib
