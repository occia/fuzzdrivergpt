#!/bin/bash

##########
# UNCOMMENT this for manual exploration on how to write this fuzzdrivergpt_build.sh
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
cat >> /src/libbpf/scripts/build-fuzzers.sh << 'EOF'
make -C src BUILD_STATIC_ONLY=y V=1 clean
make -C src -j$(nproc) CFLAGS="-I$(pwd)/elfutils/libelf $CFLAGS" BUILD_STATIC_ONLY=y V=1 OBJDIR=/src/libbpf/fuzzdrivergpt-build DESTDIR=/src/libbpf/fuzzdrivergpt-install install
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
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/libbpf/fuzzdrivergpt-install/usr/include ${INSTALL}/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/libbpf/fuzzdrivergpt-install/usr/lib64 ${INSTALL}/lib
